from unittest import TestCase

from pypubtrack.config import Config
from pypubtrack.endpoint import Endpoint, AddEndpoint


# TESTING ENDPOINT CHAINING
# =========================

class AuthorsEndpoint(Endpoint):

    def get_endpoint(self):
        return 'authors'


@AddEndpoint('author', AuthorsEndpoint)
class BooksEndpoint(Endpoint):

    def get_endpoint(self):
        return 'books'


@AddEndpoint('book', BooksEndpoint)
@AddEndpoint('author', AuthorsEndpoint)
class ChainingBase:

    url = 'http://test.com/api'
    config = Config()


class TestEndpointChaining(TestCase):

    def test_construction_books_endpoint(self):
        config = Config()
        books_endpoint = BooksEndpoint(ChainingBase.url, config)
        self.assertEqual('ENDPOINT http://test.com/api/books', str(books_endpoint))
        self.assertIsInstance(books_endpoint, BooksEndpoint)
        self.assertTrue(hasattr(books_endpoint, 'author'))

    def test_construction_chaining_base(self):
        base = ChainingBase()
        self.assertIsInstance(base, ChainingBase)
        self.assertTrue(hasattr(base, 'book'))
        self.assertTrue(hasattr(base, 'author'))

    def test_endpoint_chain(self):
        base = ChainingBase()
        self.assertIsInstance(base.book.author, Endpoint)
        self.assertEqual(
            'ENDPOINT http://test.com/api/books/title/authors',
            str(base.book('title').author)
        )
