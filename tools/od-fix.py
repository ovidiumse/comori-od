#!/usr/bin/pypy3
import os
import argparse
import yaml
from datetime import datetime
from bs4 import BeautifulSoup

PARSER_ = argparse.ArgumentParser(
    description="OD content fixer script for Hristos Puterea Apostoliei.")


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
    return tag.has_attr('style') and "{}: {}".format(attr, value) in tag['style']


def hasNestedStyleAttribute(tag, attr, value):
    for d in tag.descendants:
        if d.name == 'span' and hasStyleAttribute(d, attr, value):
            return True

    return False


def replaceNestedStyleAttribute(tag, attr, value):
    for d in tag.descendants:
        if d.name == 'span' and d.has_attr('style') and attr in d['style']:
            styles_text = d['style']
            style_pairs = styles_text.split(';')
            new_style = {}
            for pair in style_pairs:
                p, v = pair.split(':')
                new_style[p] = value if attr == p else v

            d['style'] = ";".join(["{}: {}".format(k, v) for k, v in new_style.items()])


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
            elif p == 'capitalize':
                if v != isCapitalized(tag.text):
                    return False

    return True


def isBeforeArticleTitle(tag, cfg):
    if tag.name != "p":
        return False

    for d in tag.descendants:
        if isFirstParagraphFirstLetter(d, cfg):
            return False

    return checkProps(tag, cfg['pre-before-article-title'])


def isArticleTitle(tag, cfg):
    if tag.name != "p":
        return False

    return checkProps(tag, cfg['pre-article-title'])


def isArticleSubtitle(tag, cfg):
    if tag.name != "p":
        return False

    return checkProps(tag, cfg['pre-article-subtitle'])


def isFirstParagraphFirstLetter(tag, cfg):
    if tag.name != "span":
        return False

    return checkProps(tag, cfg['pre-paragraph-first-letter'])


def printElements(soup, predicate):
    for p in soup.find_all(predicate):
        print(p.text)


def find_title(soup, cfg, last_title=None):
    if last_title:
        if 'pre-before-article-title' in cfg:
            pre_title = last_title.find_next(lambda tag: isBeforeArticleTitle(tag, cfg))
            if not pre_title:
                return None

            title = pre_title.find_next(lambda tag: isArticleTitle(tag, cfg))
        else:
            title = title.find_next(lambda tag: isArticleTitle(tag, cfg))
    else:
        if 'pre-before-article-title' in cfg:
            pre_title = soup.find(lambda tag: isBeforeArticleTitle(tag, cfg))
            if not pre_title:
                return None

            title = pre_title.find_next(lambda tag: isArticleTitle(tag, cfg))
        else:
            title = soup.find(lambda tag: isArticleTitle(tag, cfg))

    return title


def merge_multiline_titles(soup, cfg):
    print("Merging multiline titles...")

    title = find_title(soup, cfg)
    while title:
        next_p = title.find_next("p")
        if isArticleTitle(next_p, cfg):
            print("Merging {} with {}...".format(title.text, next_p.text))
            title.append(next_p.text)
            next_p.decompose()

        title = find_title(soup, cfg, title)


def merge_titles_with_subtitles(soup, cfg):
    print("Merging titles with subtitles...")

    title = find_title(soup, cfg)
    while title:
        next_p = title.find_next("p")
        if isArticleSubtitle(next_p, cfg):
            print("Merging {} with {}...".format(title.text, next_p.text))
            title.append(next_p.text)
            next_p.decompose()

        title = find_title(soup, cfg, title)


def increate_title_sizes(soup, cfg):
    print("Increasing title sizes...")

    title = find_title(soup, cfg)
    while title:
        replaceNestedStyleAttribute(title, 'font-size', '166%')
        title = find_title(soup, cfg, title)


def fix_first_paragraph_first_letters(soup, cfg):
    print("Fixing first paragraph first letters...")
    letters = soup.find_all(lambda tag: isFirstParagraphFirstLetter(tag, cfg))
    for letter in letters:
        parent = letter.find_parent()
        for d in parent.find_all():
            if len(d.get_text(strip=True)) == 0:
                d.decompose()
        for d in parent.find_all(string=True):
            if len(d.string) > 1:
                d.string.replace_with(letter.text.strip() + d.string.strip())
                break

        letter.decompose()


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

        merge_multiline_titles(soup, cfg)

        if 'pre-article-subtitle' in cfg:
            merge_titles_with_subtitles(soup, cfg)

        increate_title_sizes(soup, cfg)
        fix_first_paragraph_first_letters(soup, cfg)

        path, ext = os.path.splitext(args.html_filepath)
        fixed_filepath = "{}_fixed{}".format(path, ext)
        print("Saving results into {}...".format(fixed_filepath))
        with open(fixed_filepath, 'w', encoding='utf-8') as fixed_file:
            print(soup.prettify(), file=fixed_file)


if "__main__" == __name__:
    main()