#!/usr/bin/pypy3
import sys
import os
import re
import argparse
import simplejson as json
import yaml
from datetime import datetime
from bs4 import BeautifulSoup

PARSER_ = argparse.ArgumentParser(description="OD content extractor.")


def parseArgs():
    PARSER_.add_argument("-i",
                         "--input",
                         dest="html_filepath",
                         action="store",
                         type=str,
                         required=True,
                         help="Input html file")
    PARSER_.add_argument("-c",
                         "--cfg",
                         dest="cfg",
                         action="store",
                         type=str,
                         required=True,
                         help="Parsing config")
    PARSER_.add_argument("-a",
                         "--author",
                         dest="author",
                         action="store",
                         type=str,
                         required=True,
                         help="Book author")
    PARSER_.add_argument("-v",
                         "--volume",
                         dest="volume",
                         type=str,
                         default=None,
                         help="Volume title")
    PARSER_.add_argument("-b", "--book", dest="book", type=str, default=None, help="Book title")
    PARSER_.add_argument("-fb", "--full-book", dest="full_book", type=str, default=None, help="Full book title")
    PARSER_.add_argument("-pv",
                         "--print-volumes",
                         dest="print_volumes",
                         action="store_true",
                         default=False,
                         help="Print volume")
    PARSER_.add_argument("-pb",
                         "--print-books",
                         dest="print_books",
                         action="store_true",
                         default=False,
                         help="Print books")
    PARSER_.add_argument("-pat",
                         "--print-article-titles",
                         dest="print_article_titles",
                         action="store_true",
                         default=False,
                         help="Print article titles")
    PARSER_.add_argument("-ppt",
                         "--print-poem-titles",
                         dest="print_poem_titles",
                         action="store_true",
                         default=False,
                         help="Print poem titles")
    PARSER_.add_argument("-e",
                         "--extract-filename",
                         dest="extract_filename",
                         action="store",
                         help="Extract filename")

    return PARSER_.parse_args()


def hasStyleAttribute(tag, attr, value):
    if not tag.has_attr('style'):
        return False

    style = tag['style'].replace('\n', '').replace(': ', ':')
    if value == '*':
        return "{}:".format(attr) in style
    else:
        return "{}:{}".format(attr, value) in style


def hasNestedStyleAttribute(tag, attr, value):
    for d in tag.descendants:
        if d.name == 'span' and hasStyleAttribute(d, attr, value):
            return True

    return False


def getNestedStyleAttribute(tag, attr):
    for d in tag.descendants:
        if d.name == 'span' and d.has_attr('style') and attr in d['style']:
            props = d['style'].split(';')
            props = [prop for prop in props if attr in prop]
            prop = props[0]
            value = prop.split(':')[1].strip()
            return value
    return ""


def hasFontSize(tag, fsize):
    return hasNestedStyleAttribute(tag, 'font-size', fsize)


def hasColor(tag, color):
    return hasNestedStyleAttribute(tag, 'color', color)


def isBold(tag):
    for p in tag.parents:
        if p.name == "b" or hasStyleAttribute(p, 'font-weight', 'bold'):
            return True

    return False


def isItalic(tag):
    for p in tag.parents:
        if p.name == "i" or hasStyleAttribute(p, 'font-style', 'italic') or hasStyleAttribute(
                p, 'font-style', 'oblique'):
            return True

    return False


def getFontSize(tag):
    attr = getNestedStyleAttribute(tag, 'font-size')
    match = re.findall('[0-9]+', attr)
    if not match:
        return 0
    else:
        assert (len(match) == 1)
        return int(match[0])


def hasLetterSpacing(text, spacing):
    results = re.findall(r'(\w\w)+', text)
    if spacing == "none" and results:
        return True
    elif spacing == 1 and not results:
        return True

    return False


def isCapitalized(text):
    results = re.findall(r'[a-z]+', text)
    return not results


def checkProps(tag, cfg):
    if 'nested-style' in cfg:
        for p, v in cfg['nested-style'].items():
            if not hasNestedStyleAttribute(tag, p, v):
                return False

    if 'style' in cfg:
        for p, v in cfg['style'].items():
            if not hasStyleAttribute(tag, p, v):
                return False

    if 'other' in cfg:
        for p, v in cfg['other'].items():
            if p == 'letter-spacing':
                if not hasLetterSpacing(tag.text, v):
                    return False
            elif p == 'capitalized':
                if v != isCapitalized(tag.text):
                    return False

    return True


def isVolumeTitle(tag, cfg):
    if 'volume-title' not in cfg:
        return False

    if tag.name != "p":
        return False

    return checkProps(tag, cfg['volume-title'])


def isBookTitle(tag, cfg):
    if 'book-title' not in cfg:
        return False

    if tag.name != "p":
        return False

    return checkProps(tag, cfg['book-title'])


def isArticleTitle(tag, cfg):
    if 'article-title' not in cfg:
        return False

    if tag.name != "p":
        return False

    return checkProps(tag, cfg['article-title'])


def isArticleSubtitle(tag, cfg):
    if 'article-subtitle' not in cfg:
        return False

    if tag.name != "p":
        return False

    return checkProps(tag, cfg['article-subtitle'])


def isArticleBibleRef(tag, cfg):
    if 'article-bible-ref' not in cfg:
        return False
    
    if tag.name != 'p':
        return False
    
    return checkProps(tag, cfg['article-bible-ref'])


def isPoemTitle(tag, cfg):
    if 'poem-title' not in cfg:
        return False

    if tag.name != "p":
        return False

    return checkProps(tag, cfg['poem-title'])


def printElements(soup, predicate, cfg):
    for p in soup.find_all(lambda tag: predicate(tag, cfg)):
        print(p.text)


def printVolumeTitles(soup, cfg):
    printElements(soup, isVolumeTitle, cfg)


def printBookTitles(soup, cfg):
    printElements(soup, isBookTitle, cfg)


def printArticleTitles(soup, cfg):
    printElements(soup, isArticleTitle, cfg)


def printPoemTitles(soup, cfg):
    printElements(soup, isPoemTitle, cfg)


def getSubtitle(p, cfg):
    next_p = p.findNext('p')
    if not next_p:
        return None

    if isArticleSubtitle(next_p, cfg):
        return next_p
    else:
        return None


def extractVerse(tag):
    verse = []
    lastBlock = None
    for s in tag.find_all(string=True):
        style = []
        if isBold(s) and isItalic(s):
            style += ['bold', 'italic']
        elif isBold(s):
            style.append('bold')
        elif isItalic(s):
            style.append('italic')

        if not lastBlock:
            lastBlock = {'style': style, 'text': s.string }
        elif style != lastBlock['style']:
            verse.append(lastBlock)
            # Prepend space if not the first block of the verse
            lastBlock = {'style': style, 'text': s.string}
        else:
            lastBlock['text'] += s.string

    if lastBlock:
        verse.append(lastBlock)

    return verse

def extractArticles(soup, volume, full_book, book, author, cfg):
    articles = []

    for p in soup.find_all('p'):
        subtitle = None
        bibleRef = None
        if isBookTitle(p, cfg):
            book = p.text
        elif isArticleTitle(p, cfg) or isPoemTitle(p, cfg):
            title = p.text
            subtitle = getSubtitle(p, cfg)
            type = "poezie" if isPoemTitle(p, cfg) else "articol"
            verses = []
            lastTag = ""
            lastValue = []
            for v in p.next_elements:
                if v.name == 'p' and (isPoemTitle(v, cfg) or isArticleTitle(
                        v, cfg) or isBookTitle(v, cfg)
                                      or isVolumeTitle(v, cfg)):
                    break
                elif v.name == 'p' and isArticleSubtitle(v, cfg):
                    subtitle = v
                elif v.name == 'p' and isArticleBibleRef(v, cfg):
                    bibleRef = v
                elif v.name == 'p':
                    verse = extractVerse(v)

                    if verse or lastValue:
                        lastValue = verse
                        verses.append(lastValue)
                elif v.name == 'br' and lastTag not in ['', 'br'] and lastValue:
                    lastValue = []
                    verses.append(lastValue)

                lastTag = v.name

            if verses and not verses[-1]:
                verses = verses[:-1]

            if len(verses) > 1:
                article =  {
                    'full_book': full_book if full_book else book.strip(),
                    'book': book.strip(),
                    'author': author.strip(),
                    'title': title.strip(),
                    'verses': verses,
                    'type': type
                }

                if volume:
                    article['volume'] = volume.strip()

                if subtitle:
                    article['subtitle'] = subtitle.text.strip()
                
                if bibleRef:
                    article['bible-ref'] = bibleRef.text.strip()

                articles.append(article)

    return articles


def main():
    args = parseArgs()

    cfg = {}
    with open(args.cfg, 'r') as cfg_file:
        cfg = yaml.full_load(cfg_file)

    with open(args.html_filepath, 'r', encoding='utf-8') as html_file:
        start = datetime.now()
        print("Parsing {}...".format(args.html_filepath))
        soup = BeautifulSoup(html_file, 'html.parser')
        parse_finish = datetime.now()

        print("Parsing done in {}.".format(parse_finish - start))

        volume = None
        if args.volume:
            volume = args.volume
        else:
            volume = soup.find(lambda tag: isVolumeTitle(tag, cfg))
            if volume:
                volume = volume.text

        if args.print_volumes:
            printVolumeTitles(soup, cfg)
        if args.print_books:
            printBookTitles(soup, cfg)
        if args.print_article_titles:
            printArticleTitles(soup, cfg)
        if args.print_poem_titles:
            printPoemTitles(soup, cfg)
        if args.extract_filename:
            print("Extracting all articles...")
            articles = extractArticles(soup, volume, args.full_book, args.book, args.author, cfg)
            extract_finish = datetime.now()

            print("Extracted {} articles in {}.".format(len(articles),
                                                        extract_finish - parse_finish))

            print("Writing {} articles to {}...".format(len(articles), args.extract_filename))
            with open(args.extract_filename, 'w') as articles_file:
                json.dump(articles, articles_file, encoding=None, ensure_ascii=True, indent=2)

            text_filename = os.path.splitext(args.extract_filename)[0] + ".txt"
            with open(text_filename, 'w', encoding='utf-8') as text_file:
                for article in articles:
                    print(article['title'], file=text_file)
                    if 'subtitle' in article:
                        print("Subtitle: {}".format(article['subtitle']), file=text_file)
                    print("Author: {}".format(article['author']), file=text_file)
                    print("Book: {}".format(article['book']), file=text_file)
                    print("Full book: {}".format(article['full_book']), file=text_file)
                    if 'volume' in article:
                        print("Volume: {}".format(article['volume']), file=text_file)

                    print("Type: {}".format(article['type']), file=text_file)
                    print("", file=text_file)
                    for verse in article['verses']:
                        print(''.join([block['text'] for block in verse]), file=text_file)

                    print("", file=text_file)

        finish = datetime.now()
        print("All done in {}.".format(finish - start))


if "__main__" == __name__:
    main()
