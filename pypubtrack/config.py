import os
import toml

import pypubtrack.authentication as authentication

# CONFIG CLASS
# ============


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    """
    This is a singleton class, which implements the access to the config file.

    **Design Choice**

    So I feel like I want to explain my reasoning for this class here. This is indeed not my first implementation for
    config access within this project. Previously I was simply loading the dictionary into global variable within this
    file and then I could import this global variable and just use the dictionary.

    But while working with that implementation I have found two major problems with it:

    (1) Reloading: The problem is that the dictionary is loaded into the global variable at exactly the point when
    it is imported the first time at some other module. This means that there is no way of globally reloading the
    config to react to file system changes for example. Even if you were to assign the variable with a new dict
    for example, this change would not translate to other files! The reloaded version would only be present in a single
    file. With a singleton of course you can simply solve this problem with a "reload" method.

    (2) Reacting to change: There is a significant downside to using the config dict directly without some sort of
    intermediary layer. If you need some functionality say "CONFIG['camera']['sensor_height']" then this is the path
    which is directly implemented like this in the config file structure. This means that if you were to change the
    structure of the config file you would have to change every occasion in the code, which uses this attribute...
    This is obviously a bad SOC. With a class you could write methods, which wrap certain behaviour. After a change
    only this method would have to be changed.
    """

    def __init__(self):
        self.data = {}

    # IMPLEMENTING DICT FUNCTIONALITY
    # -------------------------------

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data.keys()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    # WRAPPER METHODS
    # ---------------

    def get_url(self) -> str:
        return self.data['basic']['url']

    def get_token(self) -> str:
        return self.data['auth']['token']

    def get_authentication_class(self) -> type:
        class_string = self.data['auth']['type']
        return getattr(authentication, class_string)

    # HELPER FUNCTIONS
    # ----------------

    def load_dict(self, data: dict):
        self.data = data

    def load_file(self, file_path: str):
        data = toml.load(file_path)
        self.load_dict(data)

