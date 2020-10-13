==========
pypubtrack
==========

.. image:: https://raw.githubusercontent.com/the16thpythonist/pypubtrack/master/main.png
        :width: 100%

.. image:: https://img.shields.io/pypi/v/pypubtrack.svg
        :target: https://pypi.python.org/pypi/pypubtrack

.. image:: https://readthedocs.org/projects/pypubtrack/badge/?version=latest
        :target: https://pypubtrack.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/the16thpythonist/pypubtrack/shield.svg
     :target: https://pyup.io/repos/github/the16thpythonist/pypubtrack/
     :alt: Updates

A python client for the pubtrack REST api

* Free software: MIT license
* Documentation: https://pypubtrack.readthedocs.io.

Table of Contents
=================

.. contents:: Table of Contents
    :depth: 3

Overview
========

`pypubtrack` is a python client interface for the PubTrack_ web applications. PubTrack is a web application, which can
be installed on a web server and which provides a web UI for tracking the scientific publications of a workgroup or
a whole institute by defining a list of observed authors. All publications published by any one of these observed
authors will be imported into the PubTrack database and a Status will be assigned based on the attributes of this
publication and a set of rules of how these attributes are *supposed to* look like.

The PubTrack web app is implemented as a REST API for the backend and a VueJS single page application as the frontend.
As it exposes a REST API, there are vast options for this client interface to interact with the application...

.. _PubTrack: https://github.com/the16thypythonist/pubtrack.git

Obtaining an API Token
----------------------

Visit the admin backend of the pubtrack site you are attempting to connect with. Navigate to the section "Tokens"
and create a new one. Use this token in your code to generate properly authenticated requests.

First Steps
===========

Installation
------------

`pypubtrack` is a pure python library and can be simply installed using pip:

.. code-block:: console

    $ pip3 install --user pypubtrack

To use the CLI commands properly it is recommended to add the folder of local binary executables to the
system PATH:

.. code-block:: console

    $ echo 'export PATH=~/.local/bin/:$PATH' >> ~/.bashrc
    $ source ~/.bashrc

Alternatively it can also be installed by cloning this repository from github and executing the setup manually:

.. code-block:: console

    $ git clone https://github.com/the16thpythonist/pypubtrack.git
    $ cd pypubtrack
    $ python3 setup.py install

Basic Usage
-----------

.. code-block:: python

    from pypubtrack import Pubtrack
    from pypubtrack.config import Config

    # Getting a new instance of the config singleton
    config = Config().load_dict({
        'basic': {'url': 'https://pubtrack.com/api/v1'},
        'auth': {'token': 'MY SUPER SECRET TOKEN'}
    })

    # Creating the main access object
    pubtrack = Pubtrack(config)

    try:
        publications = pubtrack.publication.get()['results']
        for publication in publications:
            print(publication)
    except ConnectionError:
        print('Something went wrong!')


Basic CLI Usage
---------------

If the package was properly installed, the `pypubtrack` command should be available from the terminal. For further
information use '--help' option.

.. code-block:: console

    $ pypubtrack --help

To create an installation folder and a local configuration file use the `init` command. The config file can be edited
with the `config` command. It will open in your favorite editor.

.. code-block:: console

    $ pypubtrack init
    $ pypubtrack config

To import scopus publications to your pubtrack app, use the `import-scopus` command. To update existing publication
records on pubtrack with kitopen information, use the `update-kitopen` command.

.. code-block:: console

    $ pypubtrack import-scopus --verbose --start=2018
    $ pypubtrack update-kitopen --verbose --start=2018

**(!) NOTE**

To use the pypubtrack application, the config file needs to be initialized and needs to contain valid information
about the pubtrack URL, authentication token, scopus api key etc...

Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage