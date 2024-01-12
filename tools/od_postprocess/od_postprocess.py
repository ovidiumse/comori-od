#!/usr/bin/python3
import os
import re
import sys
import argparse
import logging
import requests
import simplejson as json
import readtime
from collections import defaultdict
from unidecode import unidecode
from datetime import datetime
from prettytable import PrettyTable

BIBLE_API = "http://localhost:9002"

BIBLE = None
COMORI_API = None

PARSER_ = argparse.ArgumentParser(description="OD content post-processing.")

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
    PARSER_.add_argument("-v",
                         "--verbose",
                         dest="verbose",
                         action="store_true",
                         help="Verbose logging")

    args, _ = PARSER_.parse_known_args()
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

def replace_nbsp(val, field, isFirstBlock, isLastBlock):
    newval = val.replace(u'\xa0', ' ')
    return newval


def replace_newlines_with_spaces(val, field, isFirstBlock, isLastBlock):
    newval = val.replace('\n', ' ')
    return newval


def strip_spaces(val, field, isFirstBlock, isLastBlock):
    if not isFirstBlock and not isLastBlock:
        return val

    newval = val.lstrip() if isFirstBlock else val.rstrip()
    return newval


def replace_multiple_spaces_with_single_one(val, field, isFirstBlock, isLastBlock):
    newval = re.sub('[ \t]+', ' ', val)
    return newval


def remove_verse_numbers(val, field, isFirstBlock, isLastBlock):
    if not isLastBlock or field == 'verses':
        return val

    newval = re.sub(r'^\d+ - ', '', val)
    return newval


def remove_invalid_verses(val, field, isFirstBlock, isLastBlock):
    invalid_verses = ['T-']
    newval = '' if val in invalid_verses else val
    return newval

class WordReplacer(object):
    def __init__(self):
        self.wordReplacements = {
            'sînt': 'sunt',
            'sîntem': 'suntem',
            'sînteţi': 'sunteţi',
            'Sînt': 'Sunt',
            'Sîntem': 'Suntem',
            'Sînteţi': 'Sunteţi'
        }

        self.wordPrefixes = [
            "anti", "arhi", "atot", "auto", "bine", "contra", "des", "extra", "hiper", "hipo", "infra", "inter",
            "intra", "între", "macro", "mega", "meta", "micro", "mini", "mono", "multi", "ne", "neo", "non",
            "omni", "orto", "para", "pluri", "poli", "politico", "post", "pre", "prea", "proto", "pseudo",
            "radio", "răs", "re", "semi", "stră", "sub", "super", "supra", "tehno", "tele", "termo", "trans",
            "tri", "ultra", "uni", "vice", "nemai"
        ]

    def replace_words(self, val, field, isFirstBlock, isLastBlock):
        words = [w.strip() for w in re.findall(r'\w+', val) if w.strip()]
        words = set(words)

        replacements = []
        if words:
            for w in words:
                if w in self.wordReplacements:
                    r = self.wordReplacements[w]

                    if r != w:
                        replacements.append((w, r))
                    else:
                        logging.warn("Word {} has identical replacement!".format(w))

        if replacements:
            replacements = sorted(replacements, key=lambda t: len(t[0]), reverse=True)
            for w, r in replacements:
                val = val.replace(w, r)

        return val


    def normalize_diacritics(self, val, field, isFirstBlock, isLastBlock):
        words = [w.strip() for w in re.findall(r'\w+', val) if w.strip()]
        words = set(words)

        replacements = []
        if words:
            for w in words:
                if 'î' in w.lower():
                    if w in self.wordReplacements:
                        r = self.wordReplacements[w]
                    else:
                        r = w
                        for index, c in enumerate(r):
                            if index == 0 or index == len(r) - 1 or c.lower() != 'î':
                                continue
                            elif r[:index].lower() in self.wordPrefixes:
                                continue

                            rch = 'Â' if c == 'Î' else 'â'
                            r = r[:index] + rch + r[index + 1:]

                        if r != w:
                            self.wordReplacements[w] = r

                    if r != w:
                        replacements.append((w, r))

        if replacements:
            replacements = sorted(replacements, key=lambda t: len(t[0]), reverse=True)
            for w, r in replacements:
                val = val.replace(w, r)

        return val


def replace_words(index, val, field, isFirstBlock, isLastBlock, replacer: WordReplacer):
    replacer.replace_words(val, field, isFirstBlock, isLastBlock)


def normalize_diacritics(index, val, field, isFirstBlock, isLastBlock, replacer: WordReplacer):
    replacer.normalize_diacritics(val, field, isFirstBlock, isLastBlock)

def post_process(index, val, field, isFirstBlock, isLastBlock, replacer: WordReplacer):
    def replace_words(val, field, isFirstBlock, isLastBlock):
        return replacer.replace_words(val, field, isFirstBlock, isLastBlock)

    def normalize_diacritics(val, field, isFirstBlock, isLastBlock):
        return replacer.normalize_diacritics(val, field, isFirstBlock, isLastBlock)

    pipeline = [
        replace_nbsp, replace_newlines_with_spaces, strip_spaces,
        replace_multiple_spaces_with_single_one,
        remove_verse_numbers, remove_invalid_verses,
        replace_words, normalize_diacritics
    ]

    for p in pipeline:
        val = p(val, field, isFirstBlock, isLastBlock)

    return val


class Bible(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, uri):
        resp = requests.get("{}/{}".format(self.base_url, uri))
        resp.raise_for_status()
        return resp.json()

    def get_books(self):
        return self.get("bible/books")

    def get_aliases(self):
        return self.get("bible/books/aliases")

    def get_verses(self, bibleRef):
        return self.get("bible/{}".format(bibleRef))


class BibleRefResolver(object):
    def __init__(self, bible):
        self.bibleBooks = set([book.lower() for book in bible.get_books()])

        aliases_data = bible.get_aliases()
        book_name_variations = []
        for book, aliases in aliases_data.items():
            book_name_variations.append(book)
            book_name_variations += aliases

        book_name_variations = sorted(book_name_variations, key=lambda b: len(b), reverse=True)
        self.book_names_candidates_regex = '(?P<book_name>(' + '|'.join(book_name_variations).lower() + ')\s*)'
        self.book_names_regex = r'(?P<book_name>((\d+\s+)?[^\d\s!"\$%&\'()*+,\-.\/:;=#@?\[\\\]^_`{|}~]+\.?\s*){1,3}?)'

        self.regxGroups = {
            'chapter': r'(cap\.\s*)?(?P<chapter>\d+)\s*',
            'verse_start': r'(\s*(:|,)?\s*((v.)|(vers.)|(versetul))?\s*(?P<verse_start>\d+))?',
            'verse_end': r'(\s*-\s*(?P<verse_end>\d+)\s*)?',
            'verses': r'(\s*(:|,)?\s*(?P<verses>\s*((\s*,\s*)?\d+)+))?'
        }

        self.regex = re.compile(self.book_names_regex + ''.join([v for _, v in self.regxGroups.items()]))
        self.candidates_regex = re.compile(self.book_names_candidates_regex + ''.join([v for _, v in self.regxGroups.items()]))

        self.continuationRegex = re.compile(''.join(
            [r'(?P<prefix>(\s*(;|(şi))\s*))'] +
            [v for k, v in self.regxGroups.items() if k != 'book_name']))
        
        self.bibleCache = {}
        self.errors = []
        self.resolvedRefCnt = 0

    def has_bible_ref_candidate(self, chunk):
        return None != self.candidates_regex.search(unidecode(chunk).lower())

    def extract_book_name(self, bookName):
        return re.sub(r'^\d+\s*', '', bookName)

    def is_book_name(self, suffix):
        for book in self.bibleBooks:
            if suffix.lower().startswith(book):
                return True

        return False

    def blocks_to_text(self, blocks):
        return ' '.join([block['text'] for block in blocks])

    def verses_to_text(self, verses):
        text = ""
        for v in verses:
            text += self.blocks_to_text(v)
            text += "\n"

        return text

    def process_article(self, article):
        bibleRefs = {}
        new_verses = []
        lastVerses = []
        for verse in article['verses']:
            new_verse = self.process_verse(verse, article, bibleRefs, lastVerses)
            new_verses.append(new_verse)

            # add to lastVerses all verses since the last empty line
            if not new_verse:
                lastVerses = []
            else:
                lastVerses.append(new_verse)

        article['verses'] = new_verses
        article['bible-refs'] = bibleRefs
        return article

    def process_verse(self, verse, article, bibleRefs, lastVerses):
        new_verse = []
        for block in verse:
            new_blocks = self.process_block(block['style'], block['text'], article, bibleRefs, lastVerses + [verse])
            new_verse += new_blocks

        return new_verse

    def process_block(self, style, text, article, bibleRefs, lastVerses):
        if not text:
            return text

        resolvedRefs = self.lookup_ref_candidates(text, lambda match: self.evaluate_ref_candidate(match, article, bibleRefs, lastVerses))
        if not resolvedRefs:
            return [{'type': 'normal', 'style': style, 'text': text}]

        lastPos = 0
        blocks = []
        for match in resolvedRefs:
            # Add text between last match and current match as normal text
            textBefore = text[lastPos:match['start']]
            if textBefore:
                blocks.append({'type': 'normal', 'style': style, 'text': textBefore})

            blocks.append({'type': 'bible-ref', 'style': style, 'ref': match['ref'], 'text': match['text']})
            lastPos = match['end']

        # Add text after last match as normal text
        textAfter = text[lastPos:]
        if textAfter:
            blocks.append({'type': 'normal', 'style': style, 'text': textAfter})

        return blocks

    def evaluate_ref_candidate(self, match, article, bibleRefs, lastVerses):
        resolvedRef = self.resolve_bible_ref(match, article, lastVerses)
        if resolvedRef:
            bibleRefs[match['ref']] = resolvedRef
            return match['ref']

        return None

    def build_ref(self, matchEntry):
        ref = f"{matchEntry['book_name'].rstrip()} {matchEntry['chapter']}"
        if matchEntry['verse_start']:
            ref += f":{matchEntry['verse_start']}"
        if matchEntry['verse_end']:
            ref += f"-{matchEntry['verse_end']}"
        if matchEntry['verses']:
            if not matchEntry['verse_start']:
                ref += ":"
            else:
                ref += ", "
            ref += matchEntry['verses']

        return ref

    def build_match(self, match, lastPos):
        matchEntry = match.groupdict()
        matchEntry['text'] = match.string[match.start():match.end()]
        matchEntry['start'] = match.start() + lastPos
        matchEntry['end'] = match.end() + lastPos
        while matchEntry['text'].endswith(' '):
            matchEntry['end'] -= 1
            matchEntry['text'] = matchEntry['text'][:-1]

        return matchEntry

    def build_continuation_match(self, match, lastPos, parentEntry):
        contMatch = self.build_match(match, lastPos)
        contMatch['book_name'] = parentEntry['book_name']
        contMatch['ref'] = self.build_ref(contMatch)

        prefixLen = len(contMatch['prefix'])

        contMatch['start'] += prefixLen

        contMatch['text'] = contMatch['text'][prefixLen:]
        while contMatch['text'].endswith(' '):
            contMatch['end'] -= 1
            contMatch['text'] = contMatch['text'][:-1]

        if (contMatch['start'] - lastPos) > prefixLen:
            return None

        return contMatch

    def lookup_ref_candidates(self, text, processMatch):
        lastPos = 0
        resolvedRefs = []
        while True:
            chunk = text[lastPos:]
            if not self.has_bible_ref_candidate(chunk):
                break

            match = self.regex.search(chunk)
            if not match:
                break

            matchEntry = self.build_match(match, lastPos)
            matchEntry['ref'] = self.build_ref(matchEntry)

            bibleRef = processMatch(matchEntry)
            if bibleRef:
                matchEntry['ref'] = bibleRef
                lastPos = matchEntry['end']
                resolvedRefs.append(matchEntry)

                # Lookup continuation refs, like '1 Cor. 14, 3' followed by '; 7, 24;'
                while True:
                    chunk = text[lastPos:]
                    cMatch = self.continuationRegex.search(chunk)
                    if not cMatch:
                        break

                    contMatch = self.build_continuation_match(cMatch, lastPos, matchEntry)
                    if not contMatch:
                        break

                    # make sure there is no other following normal Bible ref overlapping the continuation match candidate
                    nextPos = lastPos
                    skip = False
                    while True:
                        chunk = text[nextPos:]
                        nextMatch = self.regex.search(chunk)
                        nextMatchRef = None
                        if not nextMatch:
                            break

                        nextMatchEntry = self.build_match(nextMatch, nextPos)
                        nextMatchEntry['ref'] = self.build_ref(nextMatchEntry)
                        nextMatchRef = processMatch(nextMatchEntry)
                        if not nextMatchRef:
                            nextPos = text.find(' ', nextMatchEntry['start'])
                            continue

                        if nextMatchEntry['start'] < contMatch['end']:
                            skip = True

                        break

                    if skip:
                        break

                    bibleRef = processMatch(contMatch)
                    if bibleRef:
                        contMatch['ref'] = bibleRef
                        resolvedRefs.append(contMatch)

                    lastPos = contMatch['end']
            else:
                lastPos = text.find(' ', matchEntry['start'])

        return resolvedRefs

    def resolve_bible_ref(self, match, article, lastVerses):
        resolvedRef = self.bibleCache.get(match['ref'])
        if resolvedRef is not None:
            return resolvedRef

        book = match['book_name'].strip()
        lookup = False
        if unidecode(book).lower() in self.bibleBooks and not isIgnoredBook(self.extract_book_name(book)):
            lookup = True

        try:
            if lookup:
                resolvedRef = BIBLE.get_verses(match['ref'])
                self.bibleCache[match['ref']] = resolvedRef
                self.resolvedRefCnt += 1
                return resolvedRef
        except requests.HTTPError as e:
            if e.response.status_code >= 400:
                logging.error("{} not found in the Bible!".format(match['ref']))

                volume = article['volume'] if 'volume' in article else '-'
                book = article['book']
                title = article['title']
                author = article['author']
                text = self.verses_to_text(lastVerses)

                error = f"Volum: {volume}\nCarte: {book}\nTitlu: {title}\nAutor: {author}\n'{match['ref']}' nu există în Biblie!\n{text}"
                self.errors.append(error)

        return None


def calculate_read_time(article):
    body = "\n".join(article['body'])
    return readtime.of_text(body).seconds


def post_process_article(article, authors_by_name):
    replacer = WordReplacer()

    article['title'] = post_process(0, article['title'], 'title', True, True, replacer)
    article['author'] = post_process(0, article['author'], 'author', True, True, replacer)

    author_data = authors_by_name.get(article['author'])
    if not author_data:
        logging.info(f"Could not find author info for {article['author']} in {', '.join(authors_by_name.keys())}")
        return

    url = author_data.get('photo-url-lg')
    if url:
        article['author-photo-url-lg'] = url

    url = author_data.get('photo-url-sm') 
    if url:
        article['author-photo-url-sm'] = url
    
    author_position = author_data.get('position')
    if author_position:
        article['author-position'] = author_position

    article['book'] = post_process(0, article['book'], 'book', True, True, replacer)
    article['full_book'] = post_process(0, article['full_book'], 'full_book', True, True, replacer)
    if 'volume' in article:
        article['volume'] = post_process(0, article['volume'], 'volume', True, True, replacer)
    new_verses = []
    lastVerse = []
    for index, verse in enumerate(article['verses']):
        new_verse = []
        for blockIndex, block in enumerate(verse):
            block['text'] = post_process(index, block['text'], 'verses', blockIndex == 0, blockIndex == len(verse) - 1, replacer)

            # Not interested in some blocks may be empty after removing nbsps, removing multiple spaces, trimming, etc.
            if block['text']:
                new_verse.append(block)

        # don't allow consecutive empty verses
        if new_verse or lastVerse:
            lastVerse = new_verse
            new_verses.append(new_verse)

    # remove last verse if empty
    if new_verses and not new_verses[-1]:
        new_verses = new_verses[:-1]

    def split(body, delim, keep=""):
        new_body = []
        for section in body:
            splits = re.split(delim, section)
            if len(splits) > 1:
                for idx, chunk in enumerate(splits):
                    # don't append separator after the last chunk
                    if idx == (len(splits) - 1):
                        new_body.append(chunk)
                    else:
                        new_body.append(chunk + keep)
            else:
                new_body.append(section)

        return [section.lstrip(' \n') for section in new_body if section.strip(' \n')]

    def split_all(body):
        dot_exceptions = [
            "cap", "păr", "pr", "dr", "dl", "sf", "Sf", "ap", "Ap", "1 Tim", "2 Tim", "1 Cor", "2 Cor", "Rom",
            "Gal", "Efes", "Ef", "Prov", "Apoc"
        ]
        dot_regex = r'(?<![A-Z])' + ''.join([f'(?<!{ex})' for ex in dot_exceptions]) + r'\.(?!\.)'

        delims = [(dot_regex, '.'), (r'\!\s*\n', "!"), ('r\?\s*\n', "?"), (r'”\n', "”"), (r'\n\n', "")]
        for delim, keep in delims:
            body = split(body, delim, keep)
        return body

    article['verses'] = new_verses
    article['body'] = split_all(
        ["\n".join(["".join([chunk['text'] for chunk in verse]) for verse in article['verses']])])
    
    article['read_time'] = calculate_read_time(article)

def process_article(article, authors_by_name, resolver: BibleRefResolver):
    print(f"Post-processing {article['book']} - {article['title']}")

    post_process_article(article, authors_by_name)
    resolver.process_article(article)

    return article
    

def post_process_articles(articles, authors_by_name, bible, args):
    resolver = BibleRefResolver(bible)
    results = [process_article(a, authors_by_name, resolver) for a in articles]
    return results, resolver.resolvedRefCnt, resolver.errors


def isIgnoredBook(book):
    ignoredBooks = ['în', 'am', 'fac']
    return book.lower() in ignoredBooks


def get_authors():
    response = requests.get(f"{COMORI_API}/od/authors")
    response.raise_for_status()
    data = response.json()

    authors_by_name = {}
    for author_bucket in data["aggregations"]["authors"]["buckets"]:
        authors_by_name[author_bucket["key"]] = author_bucket

    return authors_by_name


def main():
    args = parseArgs()

    print(f"Started od-postprocess.py on {os.path.basename(args.input)}")

    logging.basicConfig(stream=sys.stdout)
    logging.getLogger().setLevel(logging.INFO)

    global BIBLE
    global COMORI_API

    BIBLE = Bible(BIBLE_API)

    COMORI_API = os.getenv("COMORI_OD_API_HOST", "http://localhost:9000")

    logging.info(f"Loading authors from {COMORI_API}...")
    authors_by_name = get_authors()
    logging.info(f"Found authors: {', '.join([key for key in authors_by_name])}")

    start = datetime.now()
    with open(args.input, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    loading_finish = datetime.now()

    print("Loaded {} articles in {}.".format(len(articles), loading_finish - start))

    articles, refCount, errors = post_process_articles(articles, authors_by_name, BIBLE, args)
    processing_finish = datetime.now()
    print("Processed {} articles in {}.".format(len(articles), processing_finish - loading_finish))
    print("Resolved {} bible refs for {} articles.".format(refCount, len(articles)))

    titles_by_books = defaultdict(set)
    for a in articles:
        if a['title'] in titles_by_books[a['book']]:
            raise Exception(f"{a['title']} already exist in {a['book']}!")
        
        titles_by_books[a['book']].add(a['title'])

    with open(args.output, 'w') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    errors_filename = os.path.splitext(args.output)[0] + "_errors.txt"
    with open(errors_filename, 'w', encoding='utf-8') as errors_file:
        print("{} erori:\n".format(len(errors)), file=errors_file)
        for error in errors:
            print(error, file=errors_file)
            print("", file=errors_file)

    text_filepath = os.path.splitext(args.output)[0] + ".txt"
    with open(text_filepath, 'w', encoding='utf-8') as text_file:
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
                text_verse = ''.join([v['text'] for v in verse])
                print(text_verse, file=text_file)

            print("", file=text_file)

    textblocks_filepath = os.path.splitext(args.output)[0] + "_blocks.txt"
    with open(textblocks_filepath, 'w', encoding='utf-8') as text_file:
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

            text_verses = []
            for verse in article['verses']:
                text_verse = ''.join([v['text'] for v in verse])
                if text_verse:
                    text_verses.append(text_verse)

            if text_verses:
                print(" ".join(text_verses), file=text_file)

            print("", file=text_file)

    stats_filepath = os.path.splitext(args.input)[0] + "_stats.txt"
    print("Calculating article stats...")
    tbl = PrettyTable()
    tbl.field_names = ["Carte", "Titlu", "Autor", "Tip", "Numar versuri", "Numar cuvinte"]
    tbl.align['Titlu'] = 'l'
    for article in articles:
        versesCount = len(article['verses'])
        wordCount = 0
        for verse in article['verses']:
            verse = ''.join([v['text'] for v in verse])
            wordCount += len(verse.split())
        tbl.add_row([article['book'], article['title'], article['author'], article['type'], versesCount, wordCount])

    print("Writing stats to {}...".format(stats_filepath))
    with open(stats_filepath, 'w', encoding='utf-8') as stats_file:
        print("{} articles".format(len(articles)), file=stats_file)
        print(tbl, file=stats_file)

    finish = datetime.now()
    print("All done in {}.\n".format(finish - start))


if "__main__" == __name__:
    main()
