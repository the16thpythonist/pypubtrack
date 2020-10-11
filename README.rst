==========
pypubtrack
==========

.. image:: https://github.com/the16thpythonist/pypubtrack/blob/master/main.png
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

tbd

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

tbd

First Steps
===========

Installation
------------

`pypubtrack` is a pure python library and can be simply installed using pip:

.. code-block:: console

    $ pip3 install pypubtrack

Alternatively it can also be installed by cloning this repository from github and executing the setup manually:

.. code-block:: console

    $ git clone https://github.com/the16thpythonist/pypubtrack.git
    $ cd pypubtrack
    $ python3 setup.py install

Basic Usage
-----------

.. code-block:: python

    from pypubtrack import Pubtrack
    from pypubtrack.config import DEFAULT

    config = DEFAULT.copy()
    config['token'] = 'MY SUPER SECRET TOKEN'
    config['url'] = 'https://pubtrack.com/api/v1'

    pubtrack = Pubtrack(config)

    try:
        publications = pubtrack.publication.get()['results']
        for publication in publications:
            print(publication)
    except ConnectionError:
        print('Something went wrong!')


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage