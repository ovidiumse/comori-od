#!/usr/bin/pypy3
import os
import re
import argparse
import logging
import requests
import simplejson as json
from datetime import datetime
from prettytable import PrettyTable

BIBLE_API_LOCAL = "http://localhost:9001"
BIBLE_API_EXTERNAL = "http://comori-od:8001"

BIBLE = None

PARSER_ = argparse.ArgumentParser(description="OD content post-processing.")
REPLACEMENTS_STATS_ = {}


class BibleRefMatcher(object):
    def __init__(self):
        self.regxGroups = {
            'book': r'(?P<book>(\d+\s*)?[A-Z]\w+\.?((\s*)[A-Z]\w+\.?){0,2})',
            'chapter': r'\s*(cap\.)?\s*(?P<chapter>\d+)',
            'verse': r'(\s*(,|:)\s*(?P<verse>\d+))?',
            'verseEnd': r'(\s*-\s*(?P<verseEnd>\d+))?',
            'chapter2': r'((\s*(;|şi)\s*(cap\.)?(?P<chapter2>\d+))?',
            'verse2': r'(\s*(,|:)\s*(?P<verse2>\d+))',
            'verse2End': r'(-(?P<verse2End>\d+))?)?'
        }

    def compile(self):
        return re.compile(''.join([v for k, v in self.regxGroups.items()]))

    def compile_group(self, group):
        return re.compile(self.regxGroups[group])

    def compile_groups(self, groups):
        return re.compile(''.join(self.regxGroups[g] for g in groups))

    def match(self, regex, text):
        return regex.match(text)

    def match_group(self, text, group):
        return self.match(self.compile_group(group), text)

    def match_groups(self, text, groups):
        return self.match(self.compile_groups(groups), text)

    def match_all(self, text):
        return self.match(self.compile(), text)

    def find(self, regex, text):
        return [m for m in regex.finditer(text)]

    def find_group(self, text, group):
        return self.find(self.compile_group(group), text)

    def find_groups(self, text, groups):
        return self.find(self.compile_groups(groups), text)

    def find_all(self, text):
        return self.find(self.compile(), text)


class Bible(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, uri):
        resp = requests.get("{}/{}".format(self.base_url, uri))
        resp.raise_for_status()
        return resp.json()

    def get_books(self):
        return self.get("bible/books")

    def get_verses(self, bibleRef):
        return self.get("bible/{}".format(bibleRef))


def parseArgs():
    PARSER_.add_argument("-i",
                         "--input",
                         action="store",
                         type=str,
                         required=True,
                         help="Input JSON file")
    PARSER_.add_argument("-o",
                         "--output",
                         action="store",
                         default=None,
                         help="Output JSON file [default <input>_processed.json]")
    PARSER_.add_argument("-d",
                         "--delete-index",
                         dest="delete_index",
                         action="store_true",
                         help="Delete existing index")
    PARSER_.add_argument("-e",
                         "--external-host",
                         action="store_true",
                         help="Use external Bible API host")
    PARSER_.add_argument("-v",
                         "--verbose",
                         dest="verbose",
                         action="store_true",
                         help="Verbose logging")

    args = PARSER_.parse_args()
    if not args.output:
        args.output = "{}_processed.json".format(os.path.splitext(args.input)[0])

    return args


def make_replacement_info(rule_name, original, replacement, field):
    return {
        'original': original,
        'replacement': replacement,
        'rule': rule_name,
        'field': field,
        'count': 1
    }


def shorten(val):
    if len(val) > 30:
        return "{}...{}".format(val[:15], val[-15:])

    return val


def process_replacement(rule_name, original, replacement, field):
    if original != replacement:
        original = shorten(original)
        replacement = shorten(replacement)

        if original in REPLACEMENTS_STATS_ and rule_name in REPLACEMENTS_STATS_[
                original] and field in REPLACEMENTS_STATS_[original][rule_name]:
            REPLACEMENTS_STATS_[original][rule_name][field]['count'] += 1
        else:
            if original not in REPLACEMENTS_STATS_:
                REPLACEMENTS_STATS_[original] = {rule_name: {}}
            elif rule_name not in REPLACEMENTS_STATS_[original]:
                REPLACEMENTS_STATS_[original][rule_name] = {}

            REPLACEMENTS_STATS_[original][rule_name][
                field] = make_replacement_info(rule_name, original, replacement, field)


def replace_nbsp(val, field):
    newval = val.replace(u'\xa0', ' ')
    process_replacement('replace_nbsp', val, newval, field)
    return newval


def replace_newlines_with_spaces(val, field):
    newval = val.replace('\n', ' ')
    process_replacement('replace_newlines_with_spaces', val, newval, field)
    return newval


def strip_spaces(val, field):
    newval = val.strip()
    process_replacement('strip_spaces', val, newval, field)
    return newval


def replace_multiple_spaces_with_single_one(val, field):
    newval = ' '.join(val.split())
    process_replacement('replace_multiple_spaces_with_single_one', val, newval, field)
    return newval


def remove_verse_numbers(val, field):
    newval = re.sub(r'^\d+ - ', '', val)
    process_replacement('remove_verse_numbers', val, newval, field)
    return newval


wordReplacements = {
    'sînt': 'sunt',
    'sîntem': 'suntem',
    'sînteţi': 'sunteţi',
    'Sînt': 'Sunt',
    'Sîntem': 'Suntem',
    'Sînteţi': 'Sunteţi',
    'Facere': 'Facerea',
    'Tesal': 'Tes',
    'Eclesiast': 'Ecles'
}


def replace_words(val, field):
    words = [w.strip() for w in re.findall(r'\w+', val) if w.strip()]
    words = set(words)
    if words:
        for w in words:
            if w in wordReplacements:
                r = wordReplacements[w]

                if r != w:
                    val = val.replace(w, r)
                    process_replacement('replace_words', w, r, field)
                else:
                    logging.warn("Word {} has identical replacement!".format(w))

    return val


def normalize_diacritics(val, field):
    words = [w.strip() for w in re.findall(r'\w+', val) if w.strip()]
    words = set(words)
    if words:
        for w in words:
            if 'î' in w.lower():
                if w in wordReplacements:
                    r = wordReplacements[w]
                else:
                    r = w
                    for index, c in enumerate(r):
                        if index > 0 and index < len(r) - 1 and c.lower() == 'î' and not (
                                r.lower().startswith('reî') or r.lower().startswith('neî')):
                            rch = 'Â' if c == 'Î' else 'â';
                            r = r[:index] + rch + r[index + 1:]

                    if r != w:
                        wordReplacements[w] = r

                if r != w:
                    val = val.replace(w, r)
                    process_replacement('normalize_diacritics', w, r, field)

    return val


def post_process(val, field):
    pipeline = [
        replace_nbsp, replace_newlines_with_spaces, strip_spaces,
        replace_multiple_spaces_with_single_one, remove_verse_numbers, replace_words,
        normalize_diacritics
    ]

    for p in pipeline:
        val = p(val, field)

    return val


def post_process_articles(articles):
    for article in articles:
        article['title'] = post_process(article['title'], 'title')
        article['author'] = post_process(article['author'], 'author')
        article['book'] = post_process(article['book'], 'book')
        article['volume'] = post_process(article['volume'], 'volume')
        new_verses = []
        for verse in article['verses']:
            new_verses.append(post_process(verse, 'verses'))
        article['verses'] = new_verses

    return articles


def resolve_bible_refs(articles):
    bibleCache = {}
    errors = []
    matcher = BibleRefMatcher()

    refCount = 0
    for article in articles:
        new_verses = []
        bibleRefs = {}
        lastVerses = []
        lastVersesMaxSize = 3
        for verse in article['verses']:
            matches = matcher.find_all(verse)
            if matches:
                new_verse = []
                lastMatch = None
                for match in matches:
                    if not lastMatch:
                        # Add text before first match as normal text
                        text = match.string[:match.start()]
                        if text:
                            new_verse.append({'type': 'normal', 'text': text})
                    else:
                        # Add text between last match and current match as normal text
                        text = match.string[lastMatch.end():match.start()]
                        if text:
                            new_verse.append({'type': 'normal', 'text': text})

                    lastMatch = match
                    bibleRef = "{} {}".format(match.group('book'), match.group('chapter'))
                    if match.group('verse'):
                        bibleRef += ":{}".format(match.group('verse'))
                    if match.group('verseEnd'):
                        bibleRef += "-{}".format(match.group('verseEnd'))

                    new_verse.append({'type': 'bible-ref', 'text': bibleRef})
                    if bibleRef in bibleCache:
                        bibleRefs[bibleRef] = bibleCache[bibleRef]
                    else:
                        try:
                            bibleRefs[bibleRef] = bibleCache[bibleRef] = BIBLE.get_verses(bibleRef)
                        except requests.HTTPError as e:
                            if e.response.status_code == 404:
                                logging.error("{} not found in the Bible!".format(bibleRef))
                                text = '\n'.join(lastVerses + [verse])

                                template = "{volume}\n{title}\n{book} - {author}\n'{bibleRef}' nu există în Biblie:\n'{text}'"
                                errors.append(
                                    template.format(bibleRef=bibleRef,
                                                    volume=article['volume'],
                                                    title=article['title'],
                                                    book=article['book'],
                                                    author=article['author'],
                                                    text=text))
                            else:
                                pass

                # Add text after last match as normal text
                text = lastMatch.string[lastMatch.end():]
                if text:
                    new_verse.append({'type': 'normal', 'text': text})

                refCount += len(matches)
            else:
                if verse:
                    new_verse = [{'type': 'normal', 'text': verse}]
                else:
                    new_verse = []

                if verse:
                    lastVerses.append(verse)
                    if len(lastVerses) > lastVersesMaxSize:
                        lastVerses = lastVerses[lastVersesMaxSize - len(lastVerses):]

            new_verses.append(new_verse)

        article['verses'] = new_verses
        article['bible-refs'] = bibleRefs

    return articles, refCount, errors


def main():
    args = parseArgs()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    global BIBLE
    if args.external_host:
        BIBLE = Bible(BIBLE_API_EXTERNAL)
    else:
        BIBLE = Bible(BIBLE_API_LOCAL)

    start = datetime.now()
    with open(args.input, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    loading_finish = datetime.now()

    print("Loaded {} articles in {}.".format(len(articles), loading_finish - start))

    articles = post_process_articles(articles)
    processing_finish = datetime.now()
    print("Processed {} articles in {}.".format(len(articles), processing_finish - loading_finish))

    articles, refCount, errors = resolve_bible_refs(articles)
    resolving_finish = datetime.now()
    print("Resolved {} bible refs for {} articles in {}.".
          format(refCount, len(articles), resolving_finish - processing_finish))

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2)

    if errors:
        errors_filename = os.path.splitext(args.output)[0] + "_errors.txt"
        with open(errors_filename, 'w', encoding='utf-8') as errors_file:
            print("{} erori:\n".format(len(errors)), file=errors_file)
            for error in errors:
                print(error, file=errors_file)
                print("", file=errors_file)

    text_filename = os.path.splitext(args.output)[0] + ".txt"
    with open(text_filename, 'w', encoding='utf-8') as text_file:
        for article in articles:
            print(article['title'], file=text_file)
            print("Author: {}".format(article['author']), file=text_file)
            print("Book: {}".format(article['book']), file=text_file)
            print("Volume: {}".format(article['volume']), file=text_file)
            print("Type: {}".format(article['type']), file=text_file)
            print("", file=text_file)
            for verse in article['verses']:
                verse = ''.join([v['text'] for v in verse])
                print(verse, file=text_file)

            print("", file=text_file)

    stats = []
    for w, wordStats in REPLACEMENTS_STATS_.items():
        for rule, ruleStats in wordStats.items():
            for field, fieldStats in ruleStats.items():
                stats.append(fieldStats)

    stats_filepath = os.path.splitext(args.input)[0] + "_stats.txt"
    stats = sorted(stats,
                   key=lambda item: (item['count'], item['rule'], item['field']),
                   reverse=True)

    print("Writing {} replacements to {}...".format(len(REPLACEMENTS_STATS_), stats_filepath))
    tbl = PrettyTable()
    tbl.field_names = ["Cuvânt inițial", "Cuvânt înlocuitor", "Regulă", "Câmp", "Număr procesări"]
    with open(stats_filepath, 'w', encoding='utf-8') as stats_file:
        for item in stats:
            tbl.add_row([
                "'{}'".format(item['original']), "'{}'".format(item['replacement']), item['rule'],
                item['field'], item['count']
            ])
        print(tbl, file=stats_file)

    finish = datetime.now()
    print("All done in {}.".format(finish - start))


if "__main__" == __name__:
    main()