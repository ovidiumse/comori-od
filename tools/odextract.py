#!pypy3
import sys
import os
import re
import argparse
import simplejson as json
import unicodedata
from prettytable import PrettyTable
from collections import OrderedDict
from datetime import datetime
from bs4 import BeautifulSoup

PARSER_ = argparse.ArgumentParser(description="OD content extractor.")

TITLE_FSIZE = "250%"
TITLE_COLOR = "#1a8cff"

SUBTITLE_FSIZE = "250%"
SUBTITLE_COLOR = "#ff0000"

ARTICLE_TITLE_FSIZE = "208%"
ARTICLE_TITLE_COLOR = "#008000"
ARTICLE_BODY_FSIZE = "125%"

POEM_TITLE_FSIZE = "166%"
POEM_TITLE_COLOR = "#ff00ff"


def parseArgs():
    PARSER_.add_argument("-i",
                         "--input",
                         dest="html_filepath",
                         action="store",
                         type=str,
                         required=True,
                         help="Input html file")
    PARSER_.add_argument("-t", "--title", dest="title", action="store", type=str, help="Book title")
    PARSER_.add_argument("-a",
                         "--author",
                         dest="author",
                         action="store",
                         type=str,
                         required=True,
                         help="Book author")
    PARSER_.add_argument("-pt",
                         "--print-title",
                         dest="print_title",
                         action="store_true",
                         default=False,
                         help="Print title")
    PARSER_.add_argument("-ps",
                         "--print-subtitles",
                         dest="print_subtitles",
                         action="store_true",
                         default=False,
                         help="Print subtitles")
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


def hasStyleAtribute(tag, attr, value):
    return tag.has_attr('style') and "{}: {}".format(attr, value) in tag['style']


def hasNestedStyleAttribute(tag, attr, value):
    for d in tag.descendants:
        if d.name == 'span' and hasStyleAtribute(d, attr, value):
            return True

    return False


def getNestedStyleAttribute(tag, attr):
    for d in tag.descendants:
        if d.name == 'span' and tag.has_attr('style') and attr in d['style']:
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


def getFontSize(tag):
    attr = getNestedStyleAttribute(tag, 'font-size')
    match = re.findall('[0-9]+', attr)
    if not match:
        return 0
    else:
        assert(len(match) == 1)
        return int(match[0])

def isTitle(tag):
    return tag.name == "p" and hasFontSize(tag, TITLE_FSIZE) and hasColor(tag, TITLE_COLOR)


def isSubtitle(tag):
    return tag.name == "p" and hasFontSize(tag, SUBTITLE_FSIZE) and hasColor(tag, SUBTITLE_COLOR)


def isArticleTitle(tag):
    return tag.name == "p" and hasFontSize(tag, ARTICLE_TITLE_FSIZE) and hasColor(
        tag, ARTICLE_TITLE_COLOR) and hasStyleAtribute(tag, 'text-align', 'justify')


def isPoemTitle(tag):
    return tag.name == "p" and hasFontSize(tag, POEM_TITLE_FSIZE) and hasColor(
        tag, POEM_TITLE_COLOR) and hasStyleAtribute(tag, 'text-align', 'justify')


def printElements(soup, predicate):
    for p in soup.find_all(predicate):
        print(sanitizeValue(p.text))


def printTitles(soup):
    printElements(soup, isTitle)


def printSubtitles(soup):
    printElements(soup, isSubtitle)


def printArticleTitles(soup):
    printElements(soup, isArticleTitle)


def printPoemTitles(soup):
    printElements(soup, isPoemTitle)


def makeReplacement(word):
    return {'replacement': word, 'count': 0}


wordReplacements = {
    'sînt': makeReplacement('sunt'),
    'sîntem': makeReplacement('suntem'),
    'sînteţi': makeReplacement('sunteţi'),
    'Sînt': makeReplacement('Sunt'),
    'Sîntem': makeReplacement('Suntem'),
    'Sînteţi': makeReplacement('Sunteţi')
}


def sanitizeValue(val):
    val = val.replace(u'\xa0', ' ');
    val = val.replace('\n', ' ').strip()
    val = ' '.join(val.split())
    val = re.sub(r'^\d+ - ', '', val)
    words = [w.strip() for w in re.findall(r'\w+', val) if w.strip()]
    words = set(words)
    if words:
        for w in words:
            if w in wordReplacements:
                replacementInfo = wordReplacements[w]
                r = replacementInfo['replacement']
                replacementInfo['count'] += 1
            else:
                r = w
                if 'î' in r:
                    for index, c in enumerate(r):
                        if index > 0 and index < len(r) - 1 and c == 'î' and not (
                                r.startswith('reî') or r.startswith('neî')):
                            r = r[:index] + 'â' + r[index + 1:]

            if r != w:
                val = val.replace(w, r)
                if w not in wordReplacements:
                    replacementInfo = makeReplacement(r)
                    replacementInfo['count'] = 1
                    wordReplacements[w] = replacementInfo

    return val


def extractArticles(soup, volume, author):
    articles = []
    book = volume
    for p in soup.find_all('p'):
        if isSubtitle(p):
            book = sanitizeValue(p.text)
        elif isArticleTitle(p) or isPoemTitle(p):
            title = sanitizeValue(p.text)
            type = "poezie" if isPoemTitle(p) else "articol"
            verses = []
            lastTag = ""
            lastValue = ""
            for v in p.next_elements:
                if v.name == 'p' and getFontSize(v) > 125:
                    break
                elif v.name == 'p':
                    verse = sanitizeValue(v.text)
                    if verse or lastValue:
                        lastValue = sanitizeValue(v.text)
                        verses.append(lastValue)
                elif v.name == 'br' and lastTag not in ['', 'br'] and lastValue:
                    lastValue = ""
                    verses.append(lastValue)

                lastTag = v.name

            if verses and not verses[-1]:
                verses = verses[:-1]

            articles.append({
                'volume': volume,
                'book': book,
                'author': author,
                'title': title,
                'verses': verses,
                'type': type
            })

    return articles


def durationString(elapsed):
    return "{}".format(elapsed)


def main():
    args = parseArgs()

    with open(args.html_filepath, 'r', encoding='utf-8') as html_file:
        start = datetime.now()
        print("Parsing {}...".format(args.html_filepath))
        soup = BeautifulSoup(html_file, 'html.parser')
        parse_finish = datetime.now()

        print("Parsing done in {}".format(durationString(parse_finish - start)))

        p = soup.find(isTitle)
        volume = sanitizeValue(p.text)

        if args.print_title:
            printTitles(soup)
        if args.print_subtitles:
            printSubtitles(soup)
        if args.print_article_titles:
            printArticleTitles(soup)
        if args.print_poem_titles:
            printPoemTitles(soup)
        if args.extract_filename:
            print("Extracting all articles...")
            articles = extractArticles(soup, volume, args.author)
            extract_finish = datetime.now()

            print("Extracted {} articles in {}".
                  format(len(articles), durationString(extract_finish - parse_finish)))

            print("Writing {} articles to {}...".format(len(articles), args.extract_filename))
            with open(args.extract_filename, 'w') as articles_file:
                json.dump(articles, articles_file, encoding=None, ensure_ascii=True, indent=2)

            replacements_filepath = os.path.splitext(args.extract_filename)[0] + "_replacements.txt"
            replacements = OrderedDict(
                sorted(wordReplacements.items(), key=lambda i: i[1]['count'], reverse=True))

            print("Writing {} replacements to {}...".format(len(replacements),
                                                            replacements_filepath))
            tbl = PrettyTable()
            tbl.field_names = ["Cuvânt inițial", "Cuvânt înlocuitor", "Număr apariții"]
            with open(replacements_filepath, 'w', encoding='utf-8') as replacements_file:
                for word, replacementInfo in replacements.items():
                    tbl.add_row([word, replacementInfo['replacement'], replacementInfo['count']])
                print(tbl, file=replacements_file)

        finish = datetime.now()
        print("All done in {}".format(durationString(finish - start)))


if "__main__" == __name__:
    main()
