#!/usr/bin/pypy3
import re
import unittest
import simplejson as json
from od_postprocess import BIBLE_API_LOCAL, Bible, BibleRefMatcher


class TestBibleRefDetection(unittest.TestCase):
    def setUp(self):
        bible = Bible(BIBLE_API_LOCAL)
        self.books_ = bible.get_books()
        self.matcher_ = BibleRefMatcher()

    def test_book_should_match(self):
        for book in self.books_:
            match = self.matcher_.match_group(book, 'book')

            groups = match.groupdict() if match else None
            match = match.string[match.start():match.end()] if match else None

            info = "{} -> {} {}".format(book, match, groups)
            self.assertIsNotNone(match, info)
            self.assertEqual(match, book, info)

    def test_bookChapter_should_match(self):
        for book in self.books_:
            for ch in range(1, 50):
                refs = ["{} {}".format(book, ch), "{} cap. {}".format(book, ch)]
                for ref in refs:
                    match = self.matcher_.match_groups(ref, ['book', 'chapter'])

                    groups = match.groupdict() if match else None
                    match = match.string[match.start():match.end()] if match else None

                    info = "{} -> {} {}".format(ref, match, groups)
                    self.assertIsNotNone(match, info)
                    self.assertEqual(match, ref, info)

    def test_bookChapter_should_match_inside_text(self):
        for book in self.books_:
            for ch in range(1, 50):
                refs = ["{} {}".format(book, ch), "{} cap. {}".format(book, ch)]
                for ref in refs:
                    text = "Some text refering to {} then some other text.".format(ref)
                    matches = self.matcher_.find_groups(text, ['book', 'chapter'])
                    info = "{} in {} -> {}".format(
                        ref, text,
                        json.dumps([(m.string[m.start():m.end()], m.groupdict()) for m in matches], indent=2))
                    self.assertEqual(len(matches), 1, info)
                    match = matches[0]
                    self.assertEqual(match.string[match.start():match.end()], ref, info)

    def test_bookChapterVerse_should_match(self):
        for book in self.books_:
            for ch in range(1, 50):
                for v in range(1, 111):
                    refs = [
                        "{} {}:{}".format(book, ch, v), "{} {},{}".format(book, ch, v),
                        "{} {}, {}".format(book, ch, v), "{} cap. {},{}".format(book, ch, v)
                    ]
                    for ref in refs:
                        match = self.matcher_.match_groups(ref, ['book', 'chapter', 'verse'])
                        groups = match.groupdict() if match else None
                        match = match.string[match.start():match.end()] if match else None

                        info = "{} -> {} {}".format(ref, match, groups)
                        self.assertIsNotNone(match, info)
                        self.assertEqual(match, ref, info)

    def test_interestingCases_should_not_match(self):
        refs = ["1 Ioan 2-19"]
        for ref in refs:
            matches = self.matcher_.find_all(ref)
            info = "{} -> {}".format(
                refSeries, json.dumps([(m.string[m.start():m.end()], m.groupdict()) for m in matches], indent=2))
            self.assertEqual(len(matches), 0, info)

    def test_bookChapterVerseRangeSeries_should_match(self):
        refSeries = "(Colos. 2:13; Efes. 2, 1-5; 1 Tim. 5, 6; Apoc. 3, 1)."
        matches = self.matcher_.find_all(refSeries)
        info = "{} -> {}".format(
            refSeries, json.dumps([(m.string[m.start():m.end()], m.groupdict()) for m in matches], indent=2))
        self.assertEqual(len(matches), 4, info)
        self.assertEqual(matches[0], "Colos. 2:13", info)
        self.assertEqual(matches[1], "Efes. 2, 1-5", info)
        self.assertEqual(matches[2], "1 Tim. 5, 6", info)
        self.assertEqual(matches[3], "Apoc. 3, 1", info)


if __name__ == '__main__':
    unittest.main()
