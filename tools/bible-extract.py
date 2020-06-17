#!pypy3
import os
import argparse
import requests
import simplejson as json
from bs4 import BeautifulSoup, NavigableString, element

PARSER_ = argparse.ArgumentParser(description="Bible content extractor")

BIBLE_URL = "https://biblia.resursecrestine.ro/geneza"


def parseArgs():
    input_group = PARSER_.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-u", "--url", dest="url", action="store_true", help="Input url")
    input_group.add_argument("-i",
                             "--input-file",
                             dest="input_file",
                             action="store",
                             help="Input html file")
    PARSER_.add_argument("-b", "--book", dest="book", action="store", help="Bible book")
    PARSER_.add_argument("-c",
                         "--chapter",
                         dest="chapter",
                         action="store",
                         type=int,
                         help="Bible chapter")
    PARSER_.add_argument("-v", "--verse", dest="verse", action="store", help="Bible verse")
    PARSER_.add_argument("-j", "--json-file", dest="json_file", action="store", help="JSON file")
    PARSER_.add_argument("-od",
                         "--output-dir",
                         dest="output_dir",
                         action="store",
                         help="Output dir")

    args = PARSER_.parse_args()
    if args.chapter and not args.book:
        PARSER_.error("-b/--book is required if -c/--chapter is specified!")

    if args.verse and not args.chapter:
        PARSER_.error("-c/--chapter is required if -v/--verse is specified!")

    return args


def sanitizeBookName(book):
    return book.title().replace('-', ' ')


def makeBibleBook(book):
    return {'name': sanitizeBookName(book['class'][0])}


def makeBookChapter(bookTitle, chapter):
    chapter_nr = int(chapter.text.strip())
    return {
        'name': '{} {}'.format(bookTitle, chapter_nr),
        'chapter': chapter_nr,
        'link': chapter['href']
    }


def isTitleVerse(verse):
    return verse.has_attr('class') and 'versetTitlu' in verse['class']


def isVerse(verse):
    return verse.has_attr('class') and 'verset' in verse['class']


def isJesusWords(verse):
    return verse.has_attr('class') and 'Isus' in verse['class']


def isReferenceGroup(refGroup):
    return refGroup.has_attr('class') and 'trimiteriText' in refGroup['class']


def isReferenceMark(mark):
    return mark.name == 'span' and mark.has_attr('class') and 'marcaj-biblie-normal' in mark['class']


def isBibleNote(note):
    return note.name == 'span' and note.has_attr('class') and 'nota-biblie-normal' in note['class']


def isNoteMark(mark):
    return mark.name == 'sup'


def isReference(ref):
    return ref.name == 'a' and ref.has_attr('class') and 'trimitere' in ref['class']


def makeTitleVerse(verse_li):
    return {'type': 'title', 'text': verse_li.text.strip()}


def extractReferences(ref_li):
    refGroup = {}
    mark = None
    refs = []
    children = ref_li.findChildren(['span', 'a'], recursive=False)
    for c in children:
        if isReferenceMark(c):
            if mark:
                refGroup[mark] = refs
                refs = []
            mark = c.text.strip()
        elif isReference(c):
            refs.append(c.text.strip())

    if mark:
        refGroup[mark] = refs

    return refGroup


def processVerseContent(parent, type, content):
    for child in parent.children:
        if isinstance(child, NavigableString):
            content.append({'type': type, 'text': child.string})
        elif isinstance(child, element.Tag):
            if isJesusWords(child):
                processVerseContent(child, 'Jesus', content)
            elif isReferenceMark(child):
                content.append({'type': 'reference', 'text': child.text})
            elif isBibleNote(child):
                content.append({'type': 'note', 'text': child.text})


def makeVerse(chapterName, verse_li):
    verse_nr = verse_li.find('span', {'class': 'numar-verset'})
    verse_content = verse_li.find('span', {'class': 'continut-verset'})
    next = verse_li.find_next_sibling('li')

    content = []
    processVerseContent(verse_content, 'normal', content)

    return {
        'name': '{}:{}'.format(chapterName, int(verse_nr.text.strip())),
        'type': 'verse',
        'number': int(verse_nr.text.strip()),
        'content': content,
        'references': extractReferences(next) if isReferenceGroup(next) else {}
    }


def extractBibleNotes(notes_ul):
    if not notes_ul:
        return {}

    notesGroup = {}
    mark = None
    note = ""
    notes_li = notes_ul.findAll('li')
    for note_li in notes_li:
        for child in note_li.children:
            if isNoteMark(child):
                if mark:
                    notesGroup[mark] = note
                    note = ""
                mark = child.text.strip()
            elif isinstance(child, NavigableString):
                note += child.string
            else:
                note += child.text

    if mark:
        notesGroup[mark] = note

    return notesGroup


def extractVerses(chapter):
    response = requests.get(chapter['link'])
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    verses = []
    verslist = soup.find('ul', {'id': 'verslist'})
    verses_li = verslist.findAll('li')
    for verse_li in verses_li:
        if isTitleVerse(verse_li):
            verses.append(makeTitleVerse(verse_li))
        elif isVerse(verse_li):
            verses.append(makeVerse(chapter['name'], verse_li))

    chapter['verses'] = verses
    chapter['notes'] = extractBibleNotes(soup.find('ul', {'class': 'nota-subsol-biblie-normal'}))


if __name__ == "__main__":
    args = parseArgs()

    html = None
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as html_file:
            html = html_file.read()
    elif args.url:
        response = requests.get(BIBLE_URL)
        response.raise_for_status()
        html = response.text

    bible = {'name': 'Biblia Cornilescu Corectată cu trimiteri și note de subsol', 'books': []}
    soup = BeautifulSoup(html, 'html.parser')

    # extract Bible books
    chapters_index = soup.find('ul', {'class': 'col-index-chapters'})
    books_li = chapters_index.findAll('li')
    for book_li in books_li:
        book = makeBibleBook(book_li)
        if args.book and args.book != book['name']:
            continue

        chapters = []
        # extract Bible book chapters
        chapter_links = book_li.findAll('a', {'class': 'link-capitol'})
        for chapter_link in chapter_links:
            chapter = makeBookChapter(book['name'], chapter_link)
            if args.chapter and args.chapter != chapter['chapter']:
                continue

            print("Extracting {} chapter {}...".format(book['name'], chapter['chapter']))
            extractVerses(chapter)

            chapters.append(chapter)

        book['chapters'] = chapters
        bible['books'].append(book)

    if args.output_dir:
        if not os.path.exists(args.output_dir):
            print("Creating {}...".format(args.output_dir))
            os.makedirs(args.output_dir)

        for book in bible['books']:
            filename = os.path.join(args.output_dir, "{}.txt".format(book['name']))
            with open(filename, 'w', encoding='utf-8') as text_file:
                print(book['name'], file=text_file)
                for chapter in book['chapters']:
                    print("\nCap. {}\n".format(chapter['chapter']), file=text_file)
                    for verse in chapter['verses']:
                        if verse['type'] == 'title':
                            print("\n{}".format(verse['text']), file=text_file)
                        elif verse['type'] == 'verse':
                            content = [c['text'] for c in verse['content']]
                            print("{}. {}".format(verse['number'], ''.join(content)),
                                  file=text_file)

                            groups = []
                            for mark, refs in verse['references'].items():
                                groups.append("{}{}".format(mark, ';'.join(refs)))
                            if groups:
                                print("\t{}".format(' '.join(groups)), file=text_file)

                    if chapter['notes']:
                        print("\n", file=text_file)
                        for mark, note in chapter['notes'].items():
                            print("{} {}".format(mark, note), file=text_file)


        for book in bible['books']:
            filename = os.path.join(args.output_dir, "{}.json".format(book['name']))
            with open(filename, 'w') as json_file:
                json_file.write(json.dumps(book, indent=2))

    if args.json_file:
        with open(args.json_file, 'w') as json_file:
            json_file.write(json.dumps(bible, indent=2))
