import os
import sys
import inspect
from typing import Dict, Any, Type, Union

import requests


class Endpoint:

    def __init__(self, url: str, config: Dict[str, Any]):
        self.url = os.path.join(url, self.get_endpoint())
        self.config = config

    # COMPOSITE API OPERATIONS
    # ------------------------

    def post_or_get(self, data: dict, **get):
        try:
            return self.post(data)
        except ConnectionError:
            return self.get_by(**get)

    def get_by(self, **params):
        results = self.get('', params)['results']
        if len(results) == 0:
            raise FileNotFoundError('{} not found {}'.format(str(self), str(params)))
        return results[0]

    # BASIC API OPERATIONS
    # --------------------

    def delete(self, *pk: str):
        return self._request('delete', {
            'url':          self._get_url(*pk)
        })

    def put(self, *pk, data: dict = {}):
        return self._request('put', {
            'url':          self._get_url(*pk),
            'json':         data
        })

    def patch(self, *pk, patch: dict = {}):
        return self._request('patch', {
            'url':          self._get_url(*pk),
            'json':         patch
        })

    def post(self, data: dict = {}):
        return self._request('post', {
            'url':          self._get_url(),
            'json':         data
        })

    def get(self, *pk, params: dict = {}):
        return self._request('get', {
            'url':          self._get_url(*pk),
            'params':       params
        })

    # PROTECTED METHODS
    # -----------------

    def _request(self, method: str, kwargs: dict):
        kwargs = self._authentication(kwargs)

        func = getattr(requests, method)
        response = func(**kwargs)

        if response.status_code in [400]:
            print(response.json())
            raise ConnectionError('Request "{}" with status code: {} (kwargs: {})'.format(
                type,
                response.status_code,
                str(kwargs))
            )
        else:
            return response.json()

    def _get_url(self, *args):
        url = os.path.join(self.url, *args)
        if url[-1] != '/':
            url += '/'
        return url

    def _authentication(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        authenticate = self.config['authentication'](self.config)
        return authenticate(kwargs)

    # MAGIC METHODS
    # -------------

    def __call__(self, pk=''):
        self.get(pk)

    def __str__(self):
        return "ENDPOINT {}".format(self.url)

    # ABSTRACT METHODS
    # ----------------

    def get_endpoint(self):
        raise NotImplementedError()


class AddEndpoint:

    def __init__(self, name: str, endpoint: Union[Endpoint, str]):
        self.name = name
        self.endpoint = endpoint

    def __call__(self, cls: Type):

        def anonymous(this):
            if isinstance(self.endpoint, str):
                endpoint_class = self._lazy_class(self.endpoint, this.__module__)
                return endpoint_class(this.url, this.config)
            else:
                return self.endpoint(this.url, this.config)

        anonymous.__name__ = self.name
        setattr(cls, self.name, property(anonymous))

        return cls

    @classmethod
    def _lazy_class(cls, class_name: str, module: str):
        members = inspect.getmembers(sys.modules[module])
        members_dict = dict(members)
        return members_dict[class_name]
