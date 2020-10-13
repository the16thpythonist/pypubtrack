"""Main module."""
from typing import Any, Dict, Iterable

from pypubtrack.config import Config
from pypubtrack.endpoint import Endpoint, AddEndpoint
from pypubtrack.util import exclude_keys, get_config_path


# BASIC ENDPOINTS
# ===============

class AuthorsEndpoint(Endpoint):

    def get_endpoint(self):
        return 'authors'


@AddEndpoint('author', AuthorsEndpoint)
class PublicationsEndpoint(Endpoint):

    def get_endpoint(self):
        return 'publications'


class AuthoringsEndpoint(Endpoint):

    def get_endpoint(self):
        return 'authorings'


class MetaAuthorsEndpoint(Endpoint):

    def get_endpoint(self):
        return 'meta-authors'


@AddEndpoint('publication', PublicationsEndpoint)
@AddEndpoint('author', AuthorsEndpoint)
@AddEndpoint('authoring', AuthoringsEndpoint)
@AddEndpoint('meta_author', MetaAuthorsEndpoint)
class Pubtrack:
    """
    This is the main object, which represents the connection to a pubtrack web application!

    **Example**

    The following example illustrates how to initialize a new pubtrack object instance and how to use it to access a
    simple list of all publications.

    .. code-block:: python

        from pypubtrack.config import Config
        from pypubtrack.pypubtrack import Pubtrack

        # Get a new instance of the config singleton object.
        config = Config().load_dict({
            'basic': {'url': 'http://localhost/api/v1/'},
            'auth': {'token': 'my-token'}
        })

        pubtrack = Pubtrack(config)

        publications = pubtrack.publication.get()['results']
        for publication in publications:
            print(publication)

    """
    def __init__(self, config: Config):
        self.config = config
        self.url = self.config.get_url()

    # PUBLIC METHODS
    # --------------

    def import_publication(self, publication: Dict[str, Any]):
        base_publication = exclude_keys(publication, ['authors'])

        try:
            response = self.publication.post(base_publication)
            publication['uuid'] = response['uuid']
        except ConnectionError as err:
            pass

        self._import_publication_authors(publication)

    # PROTECTED_METHODS
    # -----------------

    def _import_publication_authors(self, publication: Dict[str, Any]):
        authors = publication['authors']
        authors = self._import_authors(authors)
        for author in authors:
            # Attempt to post the authorings
            data = {
                'author': author['slug'],
                'publication': publication['uuid']
            }
            self.authoring.post(data)

    def _import_authors(self, authors: Iterable[Dict[str, Any]]):
        result = []
        for author in authors:
            # The actual author
            response = self.author.post_or_get(author, scopus_id=author['scopus_id'])
            result.append(response)

        return result
