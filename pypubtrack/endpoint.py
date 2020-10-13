import os
import sys
import copy
import inspect
import urllib.parse
from typing import Dict, Any, Type, Union

import requests

from pypubtrack.config import Config


class Endpoint:
    """
    This is the base class to define a endpoint for a rest api.

    **Background**

    An "endpoint" refers to the URL, which is used to access some specific record/asset from the REST API. The
    pubtrack API exposes multiple of these endpoints to access/modify the internal database models of the app.

    **Details**

    A REST API is built on the basic HTTP protocol. All resources are in some way accessed by using these HTTP methods.
    This class implements the HTTP methods DELETE, PUT, PATCH, POST, GET to be sent to the specific endpoint, which
    is described by it. On top of that it also defines some composite methods, which combine these methods.

    This is only an abstract base class however. Every subclass has to implement the "get_endpoint" function, which
    is meant to return the concrete string URL for the specific endpoint it describes. The actual functionality of
    interaction however is universal and thus implemented in this very base class.

    **Example**

    Assume the following example of how to create an Endpoint subclass and how to for example request all of its
    results.

    .. code-block:: python

        import os

        class BooksEndpoint(Endpoint):

            def __init__(self, url, config):
                Endpoint.__init__(self, url, config)

            def get_endpoint():
                return 'books'

        # Describes the endpoint "http://myurl.com/api/books"
        books_endpoint = BooksEndpoint("http://myurl.com/api")
        books = books_endpoint.get()
        for book in books['results']:
            print(book)

    *A note on primary keys*

    Most of the methods require a primary key of the model to uniquely identify the database record on which to perform
    the action on. In terms of the previous example a "get" method with no parameters at all would return the list of
    all available books. But given a primary key, which in this case could be the string name, the method will only
    return the single record which is identified by this key.

    .. code-block:: python

        specific_book = books_endpoint.get('ultralearning')
        print(specific_book['title'])

    Now, in database modeling there is the concept of many-to-many relationships, which essentially can be illustrated
    as the "citation" relationship in the book example. A book can cite many other books, but it can also be cited by
    many other books. This kind of relationship is usually modeled as an intermediary database table called "citations"
    which has essentially two primary keys that uniquely identify the relationship. The first being the title of the
    book which cites and the second the title of the book which is cited. This kind of table would then be mapped to
    a REST API as having two primary keys "http://myurl.com/api/citation/title1/title2". This kind of resource can be
    accessed by simply passing two arguments as primary keys.

    .. code-block:: python

        specific_citation = citation_endpoint.get('ultralearning', 'thinking-fast-thinking-slow')

    """
    def __init__(self, url: str, config: Config):
        self.url = os.path.join(url, self.get_endpoint())
        self.config = config

    # BASIC API OPERATIONS
    # --------------------
    # These operations correlate directly with the basic HTTP methods with the same name.

    def delete(self, *pk: str):
        """
        Sends a DELETE request for the given primary key *pk*.
        A delete request will attempt to delete the record, which is identified by the primary key.

        :param pk:
        :return:
        """
        return self._request('delete', {
            'url':          self._get_url(*pk)
        })

    def put(self, *pk, data: dict = {}):
        """
        Sends a PUT request for the given primary key *pk* and the *data* dict.
        A put request is used to modify an already existing record which is identified by the given primary key. This
        method is essentially an "overwrite" in the sense that the existing record gets overwritten by the given data
        dict. Thus the data dict has to represent all necessary data which would have been necessary for a POST
        operation.

        :param pk:
        :param data:
        :return:
        """
        return self._request('put', {
            'url':          self._get_url(*pk),
            'json':         data
        })

    def patch(self, *pk, patch: dict = {}):
        """
        Sends a PATCH request for the given primary key *pk* and the *patch* dict.

        A patch request is used to modify an already existing record which is identified by the given primary key.
        Contrary to the put operation, the patch dict only has to contain those very attributes which are actually
        supposed to be changed.

        :param pk:
        :param patch:
        :return:
        """
        return self._request('patch', {
            'url':          self._get_url(*pk),
            'json':         patch
        })

    def post(self, data: dict = {}):
        """
        Sends a POST request for the given *data* dict.
        A post request is used to insert a new record. The data dict has to contain all the necessary information to
        construct a new record within the database of the application.

        :param data:
        :return:
        """
        return self._request('post', {
            'url':          self._get_url(),
            'json':         data
        })

    def get(self, *pk, params: dict = {}):
        """
        Sends a GET request for the given primary key *pk* and the additional get url parameters *params*.
        A get request is used to read the information of a specific record identified by the given primary key.

        For this method the primary key is optional. Calling this method without any primary keys given will return a
        list of ALL the records for that endpoint.

        :param pk:
        :param params:
        :return:
        """
        return self._request('get', {
            'url':          self._get_url(*pk),
            'params':       params
        })

    # COMPOSITE API OPERATIONS
    # ------------------------
    # These methods do not have a basic HTTP equivalent, but instead are utility functions, which are a useful
    # combination of a series of basic http methods.

    def post_or_get(self, data: dict, **get):
        """
        This method first attempts to post a new record with the given *data* dict. If this insert fails because a
        record with the given unique keys already exists, it will instead fetch this data. In any case after executing
        this method, one can be sure that a record with the given unique properties exists in the application and the
        details are returned.

        :param data:
        :param get:
        :return:
        """
        try:
            return self.post(data)
        except ConnectionError:
            return self.get_by(**get)

    def get_by(self, **params):
        """
        Retrieve a record by unique properties alternative to the primary key.

        This function simply calls the "get" method with the given *params* dict for the url parameters. The idea is
        that the REST api implements some sort of search mechanism through the url parameters and in this case
        records can be searched by secondary properties.

        :param params:
        :return:
        """
        results = self.get('', params=params)['results']
        if len(results) == 0:
            raise FileNotFoundError('{} not found {}'.format(str(self), str(params)))
        return results[0]

    # PROTECTED METHODS
    # -----------------

    def _request(self, method: str, kwargs: dict):
        """
        Executes the http method which is identified by its string name *method* with the keyword arguments in *kwargs*

        :param method:
        :param kwargs:
        :return:
        """
        # "_authentication" method adds the necessary authentication details to the kwrags dict. Otherwise it leaves
        # the dict the same
        kwargs = self._authentication(kwargs)

        # The "requests" module is a python library which implements the HTTP methods.
        # Here we dynamically invoke different methods from this module based on the string name of the http method
        # i.e. get, put, patch...
        func = getattr(requests, method)
        response = func(**kwargs)
        #print(kwargs, response.content)
        if response.status_code in [400, 403]:
            raise ConnectionError('Request "{}" with status code: {} (kwargs: {})'.format(
                method,
                response.status_code,
                str(kwargs))
            )
        else:
            # The result of the API request will be a json description of the database records, which were requested
            # "json" here is a convenience function, which returns a dict object, that was automatically json
            # parsed from the string content of the reply.
            return response.json()

    def _get_url(self, *args):
        """
        Returns the absolute url to a given endpoint, which is identified by the given *args*.

        The given *args* in this case can be a list of primary keys. So the result will be the merge of the base url
        which is saved as the "url" attribute of the object and the primary keys. This will then ultimately address
        one specific element within the web app's database.

        **Example**

        The following example illustrates how this method works.

        .. code-block:: python

            print(str(books_endpoint))
            # ENDPOINT http://myurl.com/books

            print(books_endpoint._get_url('ultralearning'))
            # http://myurl.com/books/ultralearining/

        :param args:
        :return:
        """
        # Changed 12.10.2020
        # Previously I was using "os.path.join" in this case and it was working fine, but I realized that this would
        # only be the case for linux os.
        # relative_url pre-assembles the back part of the url and "urljoin" then creates the overall correct url.
        relative_url = '/'.join(args) if args else ''
        url = '/'.join([self.url, relative_url])

        # With this we make sure that the url actually ends with a slash. In case it does not, one is added.
        # It turns out, that this is actually important!
        if url[-1] != '/':
            url += '/'

        return url

    def _authentication(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the keyword arguments to a request call and adds the necessary authentication information to it. Returns
        the kwargs dict with the added authentication.

        The type of authentication depends on the subclass of AbstractAuthentication, which was defined in the "config"
        passed to this object.

        :param kwargs:
        :return:
        """
        # "get_authentication_class" returns the class object of a subclass of AbstractAuthentication. These
        # subclasses fully implement all necessary steps for the authentication. The also implement a __call__ method
        # which adds this to the kwargs dict.
        authentication_class = self.config.get_authentication_class()
        authenticate = authentication_class(self.config)
        return authenticate(kwargs)

    # MAGIC METHODS
    # -------------

    def __call__(self, *pk):
        """
        Returns a copy of this object, where the base URL includes the given primary keys *pk*

        **Details**

        This method creates a deep copy of the very object, which it is called from. Then it changes the base API URL
        of the "url" attribute to include the primary keys which were passed as arguments to this method. This
        new instance object is then returned. The purpose of this functionality is primarily for the possibility
        of "endpoint chaining". For a detailed explanation see the class `AddEndpoint`

        **Example**

        The following example shows how a new instance is created with this method:

        .. code-block:: python

            specific_books_endpoint = books_endpoint('ultralearining')
            print(isinstance(specific_books_endpoint, Endpoint)) # True
            print(isinstance(books_endpoint, Endpoint)) # True
            print(specific_books_endpoint is books_endpoint) # False

            print(str(books_endpoint)
            # ENDPOINT http://myurl.com/api/books

            print(str(specific_books_endpoint)
            # ENDPOINT http://myurl.com/api/books/ultralearning

        :param pk:
        :return:
        """
        this = copy.deepcopy(self)
        this.url = self._get_url(*pk)
        return this

    def __str__(self):
        """
        Returns the string representation of a Endpoint object, which is simply a formatted version of the URL, which
        is returned by the "get_endpoint" method.
        :return:
        """
        return "ENDPOINT {}".format(self.url)

    # ABSTRACT METHODS
    # ----------------

    def get_endpoint(self):
        """
        This method has to be implemented by sub class!

        This method has to return the RELATIVE path towards the endpoint which is supposed to be described.
        Each endpoint object is created with a base URL which is the URL of the web applications api backend usually.
        This method is supposed to return the string of what substring has to be added to the end of this URL to
        arrive at the correct endpoint.

        :return:
        """
        raise NotImplementedError()


class AddEndpoint:
    """
    This is the class for a class decorator.

    This class can be used to add endpoints to a class as properties. The functionality is best described by an example:

    .. code-block:: python

        from pypubtrack.endpoint import Endpoint, AddEndpoint
        from pypubtrack.config import Config

        class BooksEndpoint(Endpoint):

            def __init__(self, url, config):
                Endpoint.__init__(self, url, config)

            def get_endpoint(self):
                return 'books'

        @AddEndpoint('books', BooksEndpoint)
        class Base:

            def __init__(self):
                self.config = Config()
                self.url = 'http://myurl.com/api'


        base = Base()
        print(base.books) # "ENDPOINT http://myurl.com/api/books"
        books = base.books.get()['results']

    So, the decorator requires to arguments: A string name and a Enpoint class. It will then dynamically add an endpoint
    property with the given name to the decorated class, which is an instance of the given endpoint class. The only
    requirement which has to be fulfilled by the base class which is decorated is that it does not already have a
    method/attribute with the given name and *that it has a "self.url" and "self.config" attribute* which will be used
    as the basis for the endpoint!

    *Endpoint chaining*

    This functionality also allows the chaining of endpoint classes! Let's again consider an example with the books
    endpoint. Now each book has a series of authors, but our base site also has a number of authors. So there are two
    endpoints, which we want to add: "http://myurl.com/api/books/:title/authors" and "http://myurl.com/api/authors".

    .. code-block:: python
        from pypubtrack.endpoint import Endpoint, AddEndpoint
        from pypubtrack.config import Config

        class AuthorsEndpoint(Endpoint):

            def get_endpoint(self):
                return 'authors'

        @AddEndpoint('authors', AuthorsEndpoint)
        class BooksEndpoint(Endpoint):

            def get_endpoint(self):
                return 'books'

        @AddEndpoint('books', BooksEndpoint)
        @AddEndpoint('authors', AuthorsEndpoint)
        class Base:

            def __init__(self):
                self.config = Config()
                self.url = 'http://myurl.com/api'


        base = Base()
        print(base.authors) # "ENDPOINT http://myurl.com/api/authors"
        print(base.books('title').authors) # "ENDPOINT http://myurl.com/api/books/title/authors"

    Since the "__call__" method for a Endpoint returns a modified Endpoint object instance, whose "self.url" property
    includes the given primary keys, this can be used to chain endpoints together. This enables the reuse of big chunks
    of code.

    """
    def __init__(self, name: str, endpoint: Union[Endpoint, str]):
        self.name = name
        self.endpoint = endpoint

    def __call__(self, cls: Type):
        """
        This is the method which actually performs the decoration. It accepts the class to be decorated as an argument.
        That class is modified in this function and then returned again.

        :param cls:
        :return:
        """
        # Here we dynamically construct an anonymous function object, which is actually meant to act as a method later
        # on. The "this" argument is meant to represent the "self" argument which is usually passed to methods.
        def anonymous(this):
            # If the "endpoint" definition was given as a string, this indicates that the class object of that endpoint
            # is to be lazy loaded. If the class object exists however a new endpoint instance is returned
            if isinstance(self.endpoint, str):
                # "_lazy_class' lazy loads the class object which is identified by the given string name from the
                # module IN WHICH THE DECORATION IS PERFORMED. This is important! it has to be in the same module
                endpoint_class = self._lazy_class(self.endpoint, this.__module__)
                return endpoint_class(this.url, this.config)
            else:
                return self.endpoint(this.url, this.config)

        anonymous.__name__ = self.name
        # Here we dynamically add the function which we have just defined above as a new method of the class which is
        # being decorated. In fact, the function is added as a property! This means it can be accessed as if it was a
        # attribute. It is important that is actually a function though because every call to this attribute
        # is actually meant to return a new endpoint instance!
        setattr(cls, self.name, property(anonymous))

        return cls

    @classmethod
    def _lazy_class(cls, class_name: str, module: str):
        """
        Lazy loads the class object for a given *class_name* from a module with the given *module_name*

        :param class_name:
        :param module:
        :return:
        """
        members = inspect.getmembers(sys.modules[module])
        members_dict = dict(members)
        return members_dict[class_name]
