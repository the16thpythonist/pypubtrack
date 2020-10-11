=======
History
=======

0.1.0 (2020-06-25)
------------------

- First release on PyPI.

0.2.0 (2020-10-11)
------------------

Added:

- Command Line Interface "pypubtrack"
- "init" command for the CLI. It will create an installation folder in the users home directory and also copy a
  default config file into it.
- A version file, which will store the current version of the project. It is also shipped with the project and the
  version can be viewed with the "--version" flag for the base command of the CLI
- "update-kitopen" command for CLI. It will update the pubtrack records with KITOpen database information
- Docstrings "authentication.py"
- Docstrings "endpoint.py" partial

Changed:

- The config is now managed as a singleton object instead of just a global variable dictionary.
  THIS WILL BREAK EXISTING CODE.
- Renamed "Authentication" to "AbstractAuthentication" and made it inherit from ABC
