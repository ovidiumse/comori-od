#!/usr/bin/pypy3
import os
import re
import argparse
import yaml
import hashlib
from itertools import chain
from bs4 import BeautifulSoup, element, Comment

PARSER_ = argparse.ArgumentParser(
    description="OD content fixer script")


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

    return PARSER_.parse_args()


def hasStyleAttribute(tag, attr, value):
    if not tag.has_attr('style'):
        return False

    style = tag['style'].replace('\n', '').replace(': ', ':')
    if value == '*':
        return "{}:".format(attr) in style
    else:
        return "{}:{}".format(attr, value) in style


def hasClassAttribute(tag, value):
    return tag.has_attr('class') and value in tag['class']


def hasNestedStyleAttribute(tag, attr, value):
    for d in tag.descendants:
        if d.name == 'span' and hasStyleAttribute(d, attr, value):
            return True

    return False


def replaceNestedStyleAttribute(tag, attr, value):
    for d in tag.descendants:
        if d.name == 'span':
            replaceStyleAttribute(d, attr, value)


def replaceStyleAttribute(tag, attr, value):
    if tag.has_attr('style'):
        styles_text = tag['style']
        style_pairs = styles_text.split(';')
        new_style = {}
        for pair in style_pairs:
            p, v = pair.split(':')
            new_style[p.strip()] = value if attr == p.strip() else v.strip()

        if attr not in tag['style']:
            new_style[attr] = value

        tag['style'] = ";".join(["{}: {}".format(k, v) for k, v in new_style.items()])


def removeNestedStyleAttribute(tag, attr):
    for d in tag.descendants:
        if d.name == 'span':
            removeStyleAttribute(d, attr)


def removeStyleAttribute(tag, attr):
    if tag.has_attr('style') and attr in tag['style']:
        styles_text = tag['style']
        style_pairs = styles_text.split(';')
        new_style = {}
        for pair in style_pairs:
            p, v = pair.split(':')
            if p.strip() != attr:
                new_style[p.strip()] = v.strip()

        tag['style'] = ";".join(["{}: {}".format(k, v) for k, v in new_style.items()])


def replaceProps(tag, cfg):
    if 'nested-style' in cfg:
        for prop, val in cfg['nested-style'].items():
            replaceNestedStyleAttribute(tag, prop, val)

    if 'style' in cfg:
        for prop, val in cfg['style'].items():
            replaceStyleAttribute(tag, prop, val)


def removeProps(tag, cfg):
    if 'nested-style' in cfg:
        for prop, val in cfg['nested-style'].items():
            removeNestedStyleAttribute(tag, prop)

    if 'style' in cfg:
        for prop, val in cfg['style'].items():
            removeStyleAttribute(tag, prop)


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


def isBold(tag):
    def check(tag):
        return tag.name == "b" or hasStyleAttribute(tag, 'font-weight', 'bold')

    for p in chain(tag.parents, tag.descendants if hasattr(tag, 'descendants') else []):
        if isinstance(p, element.Tag) and check(p):
            return True

    return False


def isItalic(tag):
    def check(tag):
        return tag.name == "i" \
            or hasStyleAttribute(tag, 'font-style', 'italic') \
            or hasStyleAttribute(tag, 'font-style', 'oblique')

    for p in chain(tag.parents, tag.descendants if hasattr(tag, 'descendants') else []):
        if isinstance(p, element.Tag) and check(p):
            return True

    return False


def checkProps(tag, cfg):
    if 'nested-style' in cfg:
        for p, v in cfg['nested-style'].items():
            if not hasNestedStyleAttribute(tag, p, v):
                return False

    if 'style' in cfg:
        for p, v in cfg['style'].items():
            if not hasStyleAttribute(tag, p, v):
                return False

    if 'class' in cfg:
        if not hasClassAttribute(tag, cfg['class']):
            return False
    
    if 'other' in cfg:
        for p, v in cfg['other'].items():
            if p == 'letter-spacing':
                if not hasLetterSpacing(tag.text, v):
                    return False
            elif p == 'capitalized':
                if v != isCapitalized(tag.text):
                    return False
            elif p == 'bold':
                if v != isBold(tag):
                    return False
            elif p == 'italic':
                if v != isItalic(tag):
                    return False

    return True


def isBeforeArticleTitle(tag, cfg):
    if 'pre-before-article-title' not in cfg:
        return False

    if tag.name != "p":
        return False

    for d in tag.descendants:
        if isFirstParagraphFirstLetter(d, cfg):
            return False

    return checkProps(tag, cfg['pre-before-article-title'])


def isPreArticleTitle(tag, cfg):
    props = None
    if 'pre-article-title' in cfg:
        props = cfg['pre-article-title']
    elif 'article-title' in cfg:
        props = cfg['article-title']

    if not props:
        return False

    if tag.name != "p":
        return False

    return checkProps(tag, props)


def isPrePoemTitle(tag, cfg):
    if 'poem-title' not in cfg:
        return False

    if tag.name != "p":
        return False

    return checkProps(tag, cfg['poem-title'])


def isArticleSubtitle(tag, cfg):
    if 'article-subtitle' not in cfg:
        return False

    if tag.name != "p":
        return False

    return checkProps(tag, cfg['article-subtitle'])


def isFirstParagraphFirstLetter(tag, cfg):
    if 'pre-paragraph-first-letter' not in cfg:
        return False

    if tag.name != "span":
        return False

    return checkProps(tag, cfg['pre-paragraph-first-letter'])


def isWhiteText(tag, cfg):
    return hasStyleAttribute(tag, 'color', '#ffffff') \
        or hasStyleAttribute(tag, 'color', '#FFFFFF') \
        or hasStyleAttribute(tag, 'color', 'white')


def isHardPageBreak(tag, cfg):
    return tag.name == "div" and tag.has_attr('class') and 'WPHardPageBreak' in tag['class']


def printElements(soup, predicate):
    for p in soup.find_all(predicate):
        print(p.text)


def find_title(soup, cfg, last_title=None):
    if last_title:
        if 'pre-before-article-title' in cfg:
            pre_title = last_title.find_next(lambda tag: isBeforeArticleTitle(tag, cfg))
            if not pre_title:
                return None

            title = pre_title.find_next(lambda tag: isPreArticleTitle(tag, cfg))
        else:
            title = last_title.find_next(lambda tag: isPreArticleTitle(tag, cfg))
    else:
        if 'pre-before-article-title' in cfg:
            pre_title = soup.find(lambda tag: isBeforeArticleTitle(tag, cfg))
            if not pre_title:
                return None

            title = pre_title.find_next(lambda tag: isPreArticleTitle(tag, cfg))
        else:
            title = soup.find(lambda tag: isPreArticleTitle(tag, cfg))

    return title


def sanitize_subtitle(val):
    newval = re.sub(r'^ - ', '', val)
    newval = re.sub(r' - $', '', newval)
    return newval


def fix_first_paragraph_first_letters(soup, cfg):
    print("Fixing first paragraph first letters...")

    letters = soup.find_all(lambda tag: isFirstParagraphFirstLetter(tag, cfg))
    for letter in letters:
        parent = letter.find_parent("p")

        # remove all unnecessary spaces
        for d in parent.find_all():
            if len(d.get_text(strip=True)) == 0:
                d.decompose()

        # find first string larger than 1, and prepend the letter to it
        for d in parent.find_all(string=True):
            if len(d.string) > 1:
                d.string.replace_with(letter.text.rstrip() + d.string.lstrip())
                break

        # destroy the letter element
        letter.decompose()


def remove_white_text(soup, cfg):
    print("Removing white text...")
    texts = soup.find_all(lambda tag: isWhiteText(tag, cfg))
    for t in texts:
        for d in t.find_all(string=True):
            d.string.replace_with("")


def replace_hardpagebreaks_with_breaks(soup, cfg):
    print("Removing hard breaks...")
    breaks = soup.find_all(lambda tag: isHardPageBreak(tag, cfg))
    for b in breaks:
        newBreak = soup.new_tag("br")
        b.insert_before(newBreak)
        b.decompose()


def hasCfg(tag, elementCfg):
    if tag.name != "p":
        return False

    return checkProps(tag, elementCfg)


def preprocessApply(soup, elementCfg, applyCfg):
    for p in soup.find_all(lambda tag: hasCfg(tag, elementCfg)):
        print("Transforming {}...".format(p.text))
        replaceProps(p, applyCfg)


def preprocess(soup, cfg):
    print("Preprocessing...")
    for c in cfg['preprocessing']:
        preprocessApply(soup, c['to'], c['apply'])


def sanitize_adjacent_titles(soup, cfg):
    all_titles = soup.find_all(lambda tag: isPreArticleTitle(tag, cfg) or isPrePoemTitle(tag, cfg))
    lastTitle = None
    for p in all_titles:
        if not lastTitle:
            lastTitle = p
            continue

        if isPrePoemTitle(lastTitle, cfg) and isPrePoemTitle(p, cfg):
            props = {'style': {'margin-left': '*'}}
            if (not checkProps(lastTitle, props) and checkProps(p, props)):
                removeProps(p, props)

        lastTitle = p


def remove_comments(soup):
    print("Removing comments...")
    comments = []
    ps = soup.find_all('p')
    for p in ps:
        for d in p.descendants:
            if isinstance(d, Comment):
                comments.append(d)

    for comment in comments:
        comment.extract()


def remove_anchors(soup):
    print("Removing anchors...")
    anchors = soup.find_all('a', class_='msocomanchor')
    for a in anchors:
        a.extract()


def main():
    args = parseArgs()

    print(f"Started od-fix.py on {os.path.basename(args.html_filepath)}")

    cfg = {}
    with open(args.cfg, 'r') as cfg_file:
        cfg = yaml.full_load(cfg_file)

    with open(args.html_filepath, 'r', encoding='utf-8') as html_file:
        print("Parsing {}...".format(args.html_filepath))
        soup = BeautifulSoup(html_file, 'html.parser')

        remove_comments(soup)
        remove_anchors(soup)
        sanitize_adjacent_titles(soup, cfg)

        if 'preprocessing' in cfg:
            preprocess(soup, cfg)

        fix_first_paragraph_first_letters(soup, cfg)
        remove_white_text(soup, cfg)
        replace_hardpagebreaks_with_breaks(soup, cfg)

        path, ext = os.path.splitext(args.html_filepath)
        fixed_filepath = "{}_fixed{}".format(path, ext)
        print("Saving results into {}...".format(fixed_filepath))
        with open(fixed_filepath, 'w', encoding='utf-8') as fixed_file:
            print(soup, file=fixed_file)

    print("Done!\n")


if "__main__" == __name__:
    main()