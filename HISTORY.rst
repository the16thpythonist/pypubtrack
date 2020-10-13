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


0.3.0 (2020-10-13)
------------------

Added:

- Implemented Endpoint chaining: The AddEndpoint decorator can now be used to chain endpoints together, which enable
  code reuse.
- Added unittests for the endpoint chaining functionality
- Docstrings "endpoint.py"
- The "config" CLI command. This command will edit the config file of the project
- The "import-scopus" CLI command, which will import scopus publication records based on the authors, which are defined
  on the pubtrack app
- The "list-publications" CLI command, which will list the publications on the system.
- Docstrings config file.

Fixed:

- Fixed a potential windows bug in endpoint.py
- Finally added necessary package requirements

TODO
----

- Update the README
- Write Documentation