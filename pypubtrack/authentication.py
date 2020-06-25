from typing import Dict, Any


class Authentication:

    def __init__(self, config: dict):
        self.config = config

    def __call__(self, kwargs: dict) -> Dict[str, Any]:
        return self.update_request_kwargs(kwargs)

    # TO BE IMPLEMENTED
    # -----------------

    def update_request_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        pass


class TokenAuthentication(Authentication):

    def update_request_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        token = self.config['token']
        headers = self.authentication_headers(token)

        kwargs.update({'headers': headers})
        return kwargs

    @classmethod
    def authentication_headers(cls, token):
        return {
            'Authorization': 'TOKEN {}'.format(token)
        }
