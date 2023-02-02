import re
import falcon
import simplejson as json
import logging
import urllib
from unidecode import unidecode
from datetime import datetime
from falcon.http_status import HTTPStatus

RAW_BIBLE_DATA = None
BIBLE = {}

BIBLE_ALIASES = {
    'Geneza': ['Gen', 'Gen.', 'Facerea', 'Facere', 'Fac', 'Fac.'],
    'Exodul': ['Exod', 'Exod.', 'Ex', 'Ex.', 'Iesirea', 'Iesire', 'Ies', 'Ies.'],
    'Leviticul': ['Levitic', 'Levitic.', 'Lev', 'Lev.'],
    'Numeri': ['Num', 'Num.'],
    'Deuteronomul': ['Deuteronom', 'Deuteronom.', 'Deut', 'Deut.'],
    'Iosua': ['Ios', 'Ios.'],
    'Judecatorii': ['Judecatori', 'Judec', 'Judec.', 'Jud', 'Jud.'],
    'Rut': [],
    '1 Samuel': ['1 Sam', '1 Sam.'],
    '2 Samuel': ['2 Sam', '2 Sam.'],
    '1 Imparati': ['1 Impar', '1 Impar.', '1 Imp', '1 Imp.', '1 Regi'],
    '2 Imparati': ['2 Impar', '2 Impar.', '2 Imp', '2 Imp.', '2 Regi'],
    '1 Cronici': ['1 Cron', '1 Cron.'],
    '2 Cronici': ['2 Cron', '2 Cron.'],
    'Ezra': ['Ezr', 'Ezr.'],
    'Neemia': ['Neem', 'Neem.'],
    'Estera': ['Est', 'Est.'],
    'Iov': [],
    'Psalmii': ['Psalm', 'Psalmi', 'Psalmul', 'Ps', 'Ps.'],
    'Proverbele': ['Proverbe', 'Prov', 'Prov.'],
    'Eclesiastul': ['Eclesiast', 'Ecles', 'Ecles.', 'Ecl', 'Ecl.'],
    'Cantarea Cantarilor': ['Cantarea Cant', 'Cantarea Cant.', 'Cant Cant', 'Cant. Cant.'],
    'Isaia': ['Is', 'Is.'],
    'Ieremia': ['Ierem', 'Ierem.', 'Ier', 'Ier.'],
    'Plangerile Lui Ieremia': [
        'Plangerile Lui Ierem', 'Plangerile Lui Ierem.', 'Plang Ierem', 'Plang. Ierem.', 'Plangeri',
        'Plang', 'Plang.'
    ],
    'Ezechiel': ['Ezec', 'Ezec.'],
    'Daniel': ['Dan', 'Dan.'],
    'Osea': ['Os', 'Os.'],
    'Ioel': [],
    'Amos': ['Am', 'Am.'],
    'Obadia': ['Obad', 'Obad.'],
    'Iona': [],
    'Mica': ['Mic', 'Mic.'],
    'Naum': [],
    'Habacuc': ['Habac', 'Habac.', 'Hab', 'Hab.'],
    'Tefania': ['Tefan', 'Tefan.', 'Tef', 'Tef.'],
    'Hagai': ['Hag', 'Hag.'],
    'Zaharia': ['Zahar', 'Zahar.', 'Zah', 'Zah.'],
    'Maleahi': ['Maleah', 'Maleah.', 'Mal', 'Mal.'],
    'Matei': ['Mat', 'Mat.', 'Mt', 'Mt.'],
    'Marcu': ['Mc', 'Mc.'],
    'Luca': ['Luc', 'Luc.', 'Lc', 'Lc.'],
    'Ioan': ['In', 'In.'],
    'Faptele Apostolilor': [
        'Faptele Apost.', 'Fapte', 'Fapt Ap', 'Fapt. Ap.', 'Fap Ap', 'Fap. Ap.', 'Fapt', 'Fapt.',
        'Fap', 'Fap.'
    ],
    'Romani': ['Rom', 'Rom.'],
    '1 Corinteni': ['1 Corint', '1 Corint.', '1 Cor', '1 Cor.'],
    '2 Corinteni': ['2 Corint', '2 Corint.', '2 Cor', '2 Cor.'],
    'Galateni': ['Galat', 'Galat.', 'Gal', 'Gal.'],
    'Efeseni': ['Efes', 'Efes.'],
    'Filipeni': ['Filip', 'Filip.'],
    'Coloseni': ['Colos', 'Colos.', 'Col', 'Col.'],
    '1 Tesaloniceni': ['1 Tes', '1 Tes.'],
    '2 Tesaloniceni': ['2 Tes', '2 Tes.'],
    '1 Timotei': ['1 Tim', '1 Tim.'],
    '2 Timotei': ['2 Tim', '2 Tim.'],
    'Tit': [],
    'Filimon': ['Filim', 'Filim.'],
    'Evrei': ['Evr', 'Evr.', 'Ev', 'Ev.'],
    'Iacov': ['Iac', 'Iac.', 'Ic', 'Ic.'],
    '1 Petru': ['1 Pet', '1 Pet.', '1 Pt', '1 Pt.'],
    '2 Petru': ['2 Pet', '2 Pet.', '2 Pt', '2 Pt.'],
    '1 Ioan': ['1 In', '1 In.'],
    '2 Ioan': ['2 In', '2 In.'],
    '3 Ioan': ['3 In', '3 In.'],
    'Iuda': [],
    'Apocalipsa': ['Apoc', 'Apoc.']
}

regxGroups = {
    'book_number': r'((?P<book_number>\d+)\s+)?',
    'book_name': r'(?P<book_name>([^\d\s!"\$%&\'()*+,\-.\/:;=#@?\[\\\]^_`{|}~]+\.?\s*){1,3}?)',
    'chapter': r'(cap\.\s*)?(?P<chapter>\d+)\s*',
    'verse_start': r'(\s*(:|,)?\s*((v.)|(vers.)|(versetul))?\s*(?P<verse_start>\d+))?',
    'verse_end': r'(\s*-\s*(?P<verse_end>\d+)\s*,?)?',
    'verses': r'(\s*(:|,)?\s*(?P<verses>\s*((\s*,\s*)?\d+)+))?'
}

REFERENCE_REGEX = re.compile(''.join([v for k, v in regxGroups.items()]))

class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise HTTPStatus(falcon.HTTP_200, body='\n')


class Bible(object):
    def makeChapter(self, bookName, chapter, verse=None, verse_end=None, verseNumbers=[], include_titles=False):
        return {
            'book': bookName,
            'name': chapter['name'],
            'link': chapter['link'],
            'chapter': chapter['chapter'],
            'verses': self.buildVerses(chapter, verse, verse_end, verseNumbers, include_titles)
        }

    def makeVerse(self, verse):
        r = {'type': verse['type']}
        if verse['type'] == 'verse':
            r['name'] = verse['name']
            r['number'] = verse['number']
            contents = [c['text'] for c in verse['content'] if c['type'] in ['normal', 'Jesus']]
            r['text'] = ''.join(contents)
        else:
            r['text'] = verse['text']

        return r

    def buildVerses(self, chapter, verse_start=None, verse_end=None, verseNumbers=[], include_titles=False):
        verses = []
        title_verse = None
        for verse in chapter['verses']:
            if include_titles and verse['type'] == 'title':
                title_verse = verse
            elif verse['type'] == 'verse':
                include = False
                if verse_start and verse_end and verse['number'] >= verse_start and verse['number'] <= verse_end:
                    include = True
                elif verse_start and verse['number'] == verse_start:
                    include = True
                elif verse_end and verse['number'] == verse_end:
                    include = True
                elif verse['number'] in verseNumbers:
                    include = True
                elif verse_start is None and verse_end is None and not verseNumbers: 
                    include = True

                if not include:
                    continue

                if include_titles and title_verse:
                    verses.append(title_verse)
                    title_verse = None

                verses.append(self.makeVerse(verse))

        return verses

    def make_response(self, data, callback):
        if callback:
            return "{}({})".format(callback, json.dumps(data)), "application/javascript"
        else:
            return json.dumps(data), "application/json"

    def on_get(self, req, resp, reference):
        callback = req.params['callback'] if 'callback' in req.params else None
        include_titles = req.get_param_as_bool('includeTitles')

        reference = ' '.join([word.capitalize() for word in unidecode(reference).split()])
        match = REFERENCE_REGEX.match(reference)
        if not match:
            resp.status = falcon.HTTP_404
            resp.body, resp.content_type = self.make_response(
                {
                    'message':
                    "The given reference doesn't match the <book_name> <chapter>[:<verse>[-<verseEnd>]][verse n, verse n + 1...] schema."
                }, callback)
            return

        logging.info('Looking for {}...'.format(reference))

        book_name = match.group('book_name').strip()
        if match.group('book_number'):
            book_name = "{} {}".format(match.group('book_number'), book_name)

        if book_name not in BIBLE:
            resp.status = falcon.HTTP_404
            resp.body, resp.content_type = self.make_response(
                {'message': "Book {} doesn't exist in the Bible!".format(book_name)}, callback)
            return

        book = BIBLE[book_name]
        
        chapter_nr = int(match.group('chapter'))

        verse_start = int(match.group('verse_start')) if match.group('verse_start') else None
        verse_end = int(match.group('verse_end')) if match.group('verse_end') else None
        if verse_start and verse_end and verse_end < verse_start:
            resp.status = falcon.HTTP_400
            resp.body, resp.content_type = self.make_response(
                {'message': 'Invalid verse range: {}-{}'.format(verse_start, verse_end)}, callback)
            return

        verses = []
        if len(book["chapters"]) == 1 and chapter_nr is not None and chapter_nr > 1:
            verses.append(chapter_nr)

            if verse_end and not verse_start:
                verses.append(verse_end)
                verse_end = None

            chapter_nr = 1
        
        if match.group('verses'):
            verses += [int(v.strip()) for v in match.group('verses').split(',')]
        
        if chapter_nr > len(book['chapters']):
            resp.status = falcon.HTTP_404
            resp.body, resp.content_type = self.make_response(
                {'message': "Chapter {} doesn't exist in {}!".format(chapter_nr, book_name)},
                callback)
            return

        chapter = book['chapters'][chapter_nr - 1]

        response = self.makeChapter(book['name'], chapter, verse_start, verse_end, verses, include_titles)
        if not response['verses']:
            resp.status = falcon.HTTP_404
            resp.body, resp.content_type = self.make_response(
                {'message': "Verse {} doesn't exist in {}!".format(verse_start, chapter['name'])},
                callback)
            return

        resp.status = falcon.HTTP_200
        resp.body, resp.content_type = self.make_response(response, callback)


class Books(object):
    def on_get(self, req, resp):
        results = [book for book in BIBLE]
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results)


class Aliases(object):
    def on_get(self, req, resp, book_name=None):
        resp.status = falcon.HTTP_200
        if book_name:
            resp.body = json.dumps(BIBLE_ALIASES[book_name])
        else:
            resp.body = json.dumps(BIBLE_ALIASES)


def load_app(bible_filepath):
    global RAW_BIBLE_DATA

    logging.basicConfig(level=logging.INFO)

    bibleload_start = datetime.now()
    logging.info("Loading bible from '{}'...".format(bible_filepath))
    with open(bible_filepath, 'r', encoding='utf-8') as bible_file:
        RAW_BIBLE_DATA = json.load(bible_file)
    bibleload_finish = datetime.now()
    logging.info("Loaded bible in {}".format(bibleload_finish - bibleload_start))

    logging.info("Normalizing bible data...")
    global BIBLE
    for book in RAW_BIBLE_DATA['books']:
        BIBLE[book['name']] = book
        for alias in BIBLE_ALIASES[book['name']]:
            BIBLE[alias] = book
    logging.info("Normalized bible data in {}".format(datetime.now() - bibleload_finish))

    app = falcon.API(middleware=[HandleCORS()])
    bible = Bible()
    books = Books()
    aliases = Aliases()

    app.add_route('/bible/books', books)
    app.add_route('/bible/books/aliases', aliases)
    app.add_route('/bible/books/{book_name}/aliases', aliases)
    app.add_route('/bible/{reference}', bible)

    return app