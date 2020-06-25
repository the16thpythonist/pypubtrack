==========
pypubtrack
==========


.. image:: https://img.shields.io/pypi/v/pypubtrack.svg
        :target: https://pypi.python.org/pypi/pypubtrack

.. image:: https://img.shields.io/travis/the16thpythonist/pypubtrack.svg
        :target: https://travis-ci.com/the16thpythonist/pypubtrack

.. image:: https://readthedocs.org/projects/pypubtrack/badge/?version=latest
        :target: https://pypubtrack.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/the16thpythonist/pypubtrack/shield.svg
     :target: https://pyup.io/repos/github/the16thpythonist/pypubtrack/
     :alt: Updates



A python client for the pubtrack REST api


* Free software: MIT license
* Documentation: https://pypubtrack.readthedocs.io.


Usage
-----

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
