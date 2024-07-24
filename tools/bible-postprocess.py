#!/usr/bin/pypy3
import os
import argparse
import logging
import urllib
import simplejson as json
import requests
from requests.adapters import HTTPAdapter
from collections import defaultdict
from utils import *

LOGGER_ = logging.getLogger(__name__)

PARSER_ = argparse.ArgumentParser(description="Bible content post-processor")
BIBLE_API = None

def parseArgs():
    PARSER_.add_argument("-i", "--input-file", dest="input_file", action="store", required=True, help="Input json file")
    PARSER_.add_argument("-o", "--output-file", dest="output_file", action="store", required=True, help="Output json file")
    PARSER_.add_argument("--bible-api", dest="bible_api", action="store", required=False, default=None, help="Bible API endpoint")
    PARSER_.add_argument("--bible-aliases-file", dest="bible_aliases_file", action="store", required=False, default=None, help="Bible aliases file")
    PARSER_.add_argument("--bible-root-names-file", dest="bible_root_names_file", action="store", required=False, default=None, help="Bible root names by alias file")
    PARSER_.add_argument("--bible-reverse-refs-file", dest="bible_reverse_refs_file", action="store", required=False, default=None, help="Bible reverse refs file")
    PARSER_.add_argument("--bible-refs-file", dest="bible_refs_file", action="store", required=False, default=None, help="Bible refs file")

    return PARSER_.parse_args()


def normalizeBibleRef(bibleRootNames, ref):
    refParts = ref.split(' ')
    refBookName, refPlace = (" ".join(refParts[:-1]), refParts[-1])
    refRootName = bibleRootNames.get(refBookName)
    if not refRootName:
        return None
    
    return f"{refRootName} {refPlace}"


def resolveBibleRef(session, ref):
    response = session.get(f"{BIBLE_API}/bible/{urllib.parse.quote(ref)}")
    response.raise_for_status()
    return response.json()


@timeit("Loading Bible", __name__)
def load_bible(filepath):
    LOGGER_.info(f"Loading bible from {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as json_file:
        bible = json.load(json_file)
    
    return bible

@timeit("Building articles", __name__)
def buildArticles(bible):
    LOGGER_.info("Building articles...")

    articles = []
    current_article = None

    def handlePreviousArticle():
        nonlocal current_article
        if current_article and len(current_article['verses']):
            articles.append(current_article)
            current_article = None

    for book in bible['books']:
        for chapter in book['chapters']:
            def startNewArticle(title):
                nonlocal current_article
                current_article = {}
                current_article['title'] = title
                current_article['book'] = book['name']
                current_article['chapter'] = chapter['chapter']
                current_article['chapter_link'] = chapter['link']
                current_article['verses'] = []
                current_article['body'] = ""

            handlePreviousArticle()
            startNewArticle(None)

            for verse in chapter['verses']:
                if verse['type'] == 'title':
                    handlePreviousArticle()
                    startNewArticle(verse['text'])
                elif verse['type'] == 'verse':
                    current_article['body'] += f"{verse['name']} - "
                    for chunk in verse['content']:
                        if chunk['type'] != 'reference':
                            current_article['body'] += chunk['text']
                    current_article['verses'].append(verse)
                    current_article['body'] += '\n'

    handlePreviousArticle()
    
    return articles


def hasChapter(ref):
    return len(ref.split(':')) == 2


def splitBook(ref):
    book, detail = ref.rsplit(' ', 1)
    return book, detail


def getBook(ref):
    book, _ = splitBook(ref)
    return book


def fillChapter(ref, verse, bibleRootNames):
    normalizedRef = normalizeBibleRef(bibleRootNames, ref)
    normalizedRefBook, _ = splitBook(normalizedRef)

    verseBook, chapter, _ = splitRef(verse)
    refBook, detail = splitBook(ref)
    if verseBook == normalizedRefBook:
        return f"{refBook} {chapter}:{detail}"
    else:
        return ref


def splitRef(ref):
    book, detail = ref.rsplit(' ', 1)
    chapter, verses = detail.split(':')

    return (book, chapter, verses)


def isVerseRange(verses):
    return len(verses.split('-')) == 2


def isVerseSet(verses):
    return len(verses.split(',')) > 1


def isHybrid(verses):
    return isVerseRange(verses) and isVerseSet(verses)

def splitVerseRange(verses):
    return [int(x) for x in verses.split('-')]


def splitVerseSet(verses):
    return [int(x) for x in verses.split(',')]


def areConsecutive(numbers):
    last = numbers[0] - 1
    for x in numbers:
        if last + 1 != x:
            return False
        
        last = x

    return True


def mergeRefs(verseName, lhs, rhs, bibleRootNames):
    if not hasChapter(lhs):
        lhs = fillChapter(lhs, verseName, bibleRootNames)
        if not hasChapter(lhs):
            return [lhs, rhs]
        
    if not hasChapter(rhs):
        rhs = fillChapter(rhs, verseName, bibleRootNames)
        if not hasChapter(rhs):
            return [rhs, rhs]
        
    lhsBook, lhsChapter, lhsVerses = splitRef(lhs)
    rhsBook, rhsChapter, rhsVerses = splitRef(rhs)

    def combineSingles(lhsVerses, rhsVerses):
        if int(lhsVerses) + 1 == int(rhsVerses):
            return [f"{lhsBook} {lhsChapter}:{lhsVerses}-{rhsVerses}"]
        else:
            return [f"{lhsBook} {lhsChapter}:{lhsVerses},{rhsVerses}"]

    def combineRanges(lhsVerses, rhsVerses):
        lhsVerseFrom, lhsVerseTo = splitVerseRange(lhsVerses)
        rhsVerseFrom, rhsVerseTo = splitVerseRange(rhsVerses)

        if lhsVerseTo + 1 == rhsVerseFrom or lhsVerseTo == rhsVerseFrom:
            return [f"{lhsBook} {lhsChapter}:{lhsVerseFrom}-{rhsVerseTo}"]
        else:
            return [lhs, rhs]
        
    def combineRangeAndSet(lhsVerses, rhsVerses):
        lhsVerseFrom, lhsVerseTo = splitVerseRange(lhsVerses)
        rhsVerseNumbers = splitVerseSet(rhsVerses)
        if lhsVerseTo + 1 == rhsVerseNumbers[0] or lhsVerseTo == rhsVerseNumbers[0] and areConsecutive(rhsVerseNumbers):
            return [f"{lhsBook} {lhsChapter}:{lhsVerseFrom}-{rhsVerseNumbers[-1]}"]
        else:
            return [f"{lhsBook} {lhsChapter}:{lhsVerses},{rhsVerses}"]
        
    def combineRangeAndSingle(lhsVerses, rhsVerses):
        lhsVerseFrom, lhsVerseTo = splitVerseRange(lhsVerses)
        if lhsVerseTo + 1 == int(rhsVerses) or lhsVerseTo == int(rhsVerses):
            return [f"{lhsBook} {lhsChapter}:{lhsVerseFrom}-{rhsVerses}"]
        else:
            return [f"{lhsBook} {lhsChapter}:{lhsVerses},{rhsVerses}"]
        
    def combineSets(lhsVerses, rhsVerses):
        return [f"{lhsBook} {lhsChapter}:{lhsVerses},{rhsVerses}"]
    
    def combineSetAndSingle(lhsVerses, rhsVerses):
        return [f"{lhsBook} {lhsChapter}:{lhsVerses},{rhsVerses}"]

    if lhsBook == rhsBook and lhsChapter == rhsChapter:
        if not (isVerseRange(lhsVerses) or isVerseRange(rhsVerses)) and not (isVerseSet(lhsVerses) or isVerseSet(rhsVerses)):
            return combineSingles(lhsVerses, rhsVerses)
        else:
            if isHybrid(lhsVerses) and isHybrid(rhsVerses):
                return [lhs, rhs]
            elif isHybrid(lhsVerses) and isVerseRange(rhsVerses):
                return [lhs, rhs]  
            elif isHybrid(lhsVerses):
                return [f"{lhsBook} {lhsChapter}:{lhsVerses},{rhsVerses}"]
            elif isVerseRange(lhsVerses) and isVerseRange(rhsVerses):
                return combineRanges(lhsVerses, rhsVerses)
            elif isVerseRange(lhsVerses) and isVerseSet(rhsVerses):
                return combineRangeAndSet(lhsVerses, rhsVerses)
            elif isVerseRange(lhsVerses):
                return combineRangeAndSingle(lhsVerses, rhsVerses)
            elif isVerseSet(lhsVerses) and isVerseRange(rhsVerses):
                return [lhs, rhs]
            elif isVerseSet(lhsVerses) and isVerseSet(rhsVerses):
                return combineSets(lhsVerses, rhsVerses)
            elif isVerseSet(lhsVerses):
                return combineSetAndSingle(lhsVerses, rhsVerses)
            else:
                return [lhs, rhs]
    
    return [lhs, rhs]
    

@timeit("Compacting refs", __name__)
def compactRefs(articles, bibleRootNames):
    for a in articles:
        for verse in a['verses']:
            if verse['type'] != 'verse':
                continue

            for key, refs in verse['references'].items():
                newRefs = []
                lastRef = None
                for ref in refs:
                    if not lastRef:
                        lastRef = ref
                        continue

                    refMerge = mergeRefs(verse['name'], lastRef, ref, bibleRootNames)
                    if len(refMerge) == 1:
                        lastRef = refMerge[0]
                    else:
                        newRefs.append(lastRef)
                        lastRef = ref

                if lastRef:
                    newRefs.append(lastRef)
            
                verse['references'][key] = newRefs


@timeit("Building Bible book aliases", __name__)
def buildBookAliases():
    LOGGER_.info("Building book aliases...")
    
    response = requests.get(f"{BIBLE_API}/bible/books/aliases")
    response.raise_for_status()
    bookAliases = response.json()
    return bookAliases


@timeit("Building Bible root names by alias", __name__)
def buildBibleRootNamesByAlias():
    LOGGER_.info("Building Bible root names by alias...")

    response = requests.get(f"{BIBLE_API}/bible/books/aliases")
    response.raise_for_status()
    bookAliases = response.json()
    result = {}
    for rootName, aliases in bookAliases.items():
        for alias in aliases:
            result[alias] = rootName
        
        # add the given ref itself, so that short book names like Ioel resolve to Ioel
        result[rootName] = rootName

    return result


@timeit("Building Bible reverse refs", __name__)
def buildBibleReverseRefs(articles, bibleRootNames):
    LOGGER_.info("Building Bible reverse refs...")

    result = defaultdict(list)

    for a in articles:
        for verse in a['verses']:
            for _, refs in verse['references'].items():
                for ref in refs:
                    normalizedRef = normalizeBibleRef(bibleRootNames, ref)
                    if not normalizedRef:
                        LOGGER_.warn(f"No normalized ref found for {ref}!")
                    else:
                        result[normalizedRef].append(verse['name'])

    return result


@timeit("Building Bible refs", __name__)
def buildBibleRefs(articles, bibleRootNames, bibleReverseRefs):
    LOGGER_.info("Building and resolving Bible refs...")
    
    result = dict()

    with requests.session() as session:
        prevBook = None
        for a in articles:
            if a['book'] != prevBook:
                LOGGER_.info(f"Building Bible refs for {a['book']}")
                prevBook = a['book']

            for verse in a['verses']:
                if verse['type'] == 'verse':
                    for _, refs in verse['references'].items():
                        for ref in refs:
                            if ref in result:
                                continue

                            if not hasChapter(ref):
                                ref = fillChapter(ref, verse['name'], bibleRootNames)

                            normalizedRef = normalizeBibleRef(bibleRootNames, ref)
                            if not normalizedRef:
                                LOGGER_.warning(f"No normalized ref found for {ref}!")

                            try:
                                resolvedRef = resolveBibleRef(session, normalizedRef)
                                result[ref] = resolvedRef
                            except Exception as e:
                                LOGGER_.warning(f"Resolving {ref} of {verse['name']} normalized to {normalizedRef} failed! Error: {e}")
    
        LOGGER_.info(f"Resolving reverse refs...")
        for _, refs in bibleReverseRefs.items():
            for ref in refs:
                if ref not in result:
                    normalizedRef = normalizeBibleRef(bibleRootNames, ref)
                    if not normalizedRef:
                        LOGGER_.warning(f"No normalized ref found for {ref}!")

                    try:
                        resolvedRef = resolveBibleRef(session, normalizedRef)
                        result[ref] = resolvedRef
                    except Exception as e:
                        LOGGER_.warning(f"Resolving {ref} of {verse['name']} normalized to {normalizedRef} failed! Error: {e}")

    return result


@timeit("Writing Bible", __name__)
def writeBible(articles, outputFile):
    with open(outputFile, 'w') as outputFile:
        outputFile.write(json.dumps(articles, indent=2))


@timeit("Writing Bible aliases", __name__)
def writeBibleAliases(bibleAliases, bibleAliasesFile):
    with open(bibleAliasesFile, 'w') as outputFile:
        outputFile.write(json.dumps(bibleAliases, indent=2))


@timeit("Writing Bible root names by alias", __name__)
def writeBibleRootNames(bibleRootNames, bibleRootNamesFile):
    with open(bibleRootNamesFile, 'w') as outputFile:
        outputFile.write(json.dumps(bibleRootNames, indent=2))


@timeit("Writing Bible reverse refs", __name__)
def writeBibleReverseRefs(bibleReverseRefs, bibleReverseRefsFile):
    with open(bibleReverseRefsFile, 'w') as outputFile:
        outputFile.write(json.dumps(bibleReverseRefs, indent=2))


@timeit("Writing Bible refs", __name__)
def writeBibleRefs(bibleRefs, bibleRefsFile):
    with open(bibleRefsFile, 'w') as outputFile:
        outputFile.write(json.dumps(bibleRefs, indent=2))

def main():
    args = parseArgs()

    global BIBLE_API
    if args.bible_api:
        BIBLE_API = args.bible_api
    else:
        BIBLE_API = os.environ.get("BIBLE_API")

    if not BIBLE_API:
        raise Exception("Bible API not provided!")

    logging.basicConfig(level = logging.INFO)

    LOGGER_.info(f"Started bible-postprocess.py on ${args.input_file}")
    
    bible = load_bible(args.input_file)

    articles = buildArticles(bible)

    bibleRootNames = buildBibleRootNamesByAlias()
    compactRefs(articles, bibleRootNames)

    writeBible(articles, args.output_file)

    if args.bible_aliases_file:
        bibleAliases = buildBookAliases()
        writeBibleAliases(bibleAliases, args.bible_aliases_file)

    if args.bible_root_names_file:
        writeBibleRootNames(bibleRootNames, args.bible_root_names_file)

    if args.bible_reverse_refs_file:
        bibleReverseRefs = buildBibleReverseRefs(articles, bibleRootNames)
        writeBibleReverseRefs(bibleReverseRefs, args.bible_reverse_refs_file)

    if args.bible_refs_file:
        bibleRefs = buildBibleRefs(articles, bibleRootNames, bibleReverseRefs)
        writeBibleRefs(bibleRefs, args.bible_refs_file)

if __name__ == "__main__":
    main()