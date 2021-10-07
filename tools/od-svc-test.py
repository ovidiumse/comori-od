#!/usr/bin/pypy3
import sys
import os
import unittest
import string
import random
import requests
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

global BASE_URL

class Client:
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        self.uid = 'testuser'
        self.key = os.environ.get("TEST_APP_KEY")
    
    def makeAuth(self):
        auth = {
            'iss': 'comori-od-unittest',
            'sub': self.uid,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(minutes=1)
        }

        return jwt.encode(auth, key=self.key, algorithm="ES512")

    def get(self, uri):
        response = requests.get(self.baseUrl + uri, headers={'Authorization': self.makeAuth()})
        response.raise_for_status()

        return response.json()

    def post(self, uri, data):
        response = requests.post(self.baseUrl + uri, headers={'Authorization': self.makeAuth()}, json=data)
        response.raise_for_status()

        return response.json()

    def delete(self, uri):
        response = requests.delete(self.baseUrl + uri, headers={'Authorization': self.makeAuth()})
        response.raise_for_status()


class TestFavorites(unittest.TestCase):
    def setUp(self):
        self.client_ = Client(BASE_URL)
        print(f"Client initialized with BASE_URL: {BASE_URL}")

    def generateFav(self):
        random.seed()

        tags = []
        for _ in range(1, random.choice(range(1, 4))):
            tags.append("".join(random.choices(string.ascii_letters, k=random.choice(range(3, 10)))))

        authors = ["Traian Dorz", "Pr. Iosif Trifa"]
        books = ["Cantari", "Cugetari", "Avutia Sfantului Mostenitor"]

        return {
            'id': "".join(random.choices(string.ascii_letters + string.digits, k=16)),
            'title': "".join(random.choices(string.ascii_letters + '-', k=10)),
            'tags': tags,
            'author': random.choice(authors),
            'book': random.choice(books)
        }
    
    def get(self):
        return self.client_.get('favorites')

    def post(self, data):
        return self.client_.post('favorites', data)
    
    def delete(self, id):
        self.client_.delete(f'favorites/{id}')

    def test_createFavs(self):
        # no favs initially
        favs = self.get()
        self.assertFalse(favs)

        # generate 1 .. 20 favs
        generatedFavs = []
        for _ in range(0, random.choice(range(1, 20))):
            generatedFavs.append(self.generateFav())

        # upload generated favs
        for fav in generatedFavs:
            self.post(fav)

        # get favs from server and compare
        favs = self.get()
        self.assertEqual(len(favs), len(generatedFavs))
        for fav in favs:
            self.assertTrue('timestamp' in fav)
            del fav['timestamp']
        
        # delete favs
        self.assertEqual(favs, generatedFavs)
        for fav in favs:
            self.delete(fav['id'])
        
        # get favs again
        favs = self.get()
        self.assertFalse(favs)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: od-svc-test.py [dotenvFilepath] [baseUrl]")
        exit(1)
    
    dotenv_filePath = args[0]
    if dotenv_filePath:
        load_dotenv(dotenv_filePath)

    if len(args) > 1:
        BASE_URL = args[1]
    else:
        BASE_URL = "http://localhost:9000/od/"

    unittest.main(argv=[sys.argv[0]], exit=False)