import os
import shutil
import datetime

from pathlib import Path
from typing import Iterable, Dict, Any

import click
from jinja2 import Template
from pybliometrics.scopus import AbstractRetrieval


PATH = Path(__file__).parent.absolute()
TEMPLATE_PATH = os.path.join(PATH, 'templates')


# INSTALLATION UTILITIES
# ======================

def get_home_path() -> str:
    return str(Path.home())


def get_installation_path() -> str:
    # TODO: I think I would need to change this for windows and MAC?
    home_path = get_home_path()
    # Linux
    return os.path.join(home_path, '.pypubtrack')


def get_config_path() -> str:
    folder_path = get_installation_path()
    return os.path.join(folder_path, 'config.toml')


def check_installation() -> bool:
    installation_path = get_installation_path()
    return os.path.exists(installation_path) and os.path.isdir(installation_path)


def init_installation() -> str:
    # Create a new folder
    folder_path = get_installation_path()
    os.mkdir(folder_path, 0o777)

    # Copy the default config file into it
    config_template_path = os.path.join(PATH, 'templates', 'config.toml')
    config_path = get_config_path()
    shutil.copyfile(config_template_path, config_path)

    # Copy the version file into it
    version_template_path = os.path.join(PATH, 'VERSION')
    version_path = os.path.join(folder_path, 'VERSION')
    shutil.copyfile(version_template_path, version_path)

    return folder_path


# DICT UTILITIES
# ==============

def exclude_keys(d: Dict[Any, Any], keys: Iterable[Any]) -> Dict[Any, Any]:
    copy = d.copy()
    for key in keys:
        del copy[key]

    return copy


# OUTPUT UTILITIES
# ================

def get_template(name: str):
    template_path = os.path.join(TEMPLATE_PATH, name)
    with open(template_path, mode='r+') as file:
        return Template(file.read())


def out(verbose: bool, *args, **kwargs):
    if verbose:
        click.secho(*args, **kwargs)


def get_version() -> str:
    version_path = os.path.join(PATH, 'VERSION')
    with open(version_path, mode='r') as file:
        return file.read().replace('\n', '').replace(' ', '')


# MISC. UTILITIES
# ===============


def author_name_kitopen(first_name: str, last_name: str) -> str:
    return '{}, {}*'.format(
        last_name.upper(),
        first_name[0].upper()
    )


class ScopusPublicationAdapter:

    def __init__(self, abstract_retrieval: AbstractRetrieval):
        self.abstract_retrieval = abstract_retrieval

    def get_publication(self):
        return {
            'title': self.abstract_retrieval.title,
            'published': self._convert_date(self.abstract_retrieval.coverDate),
            'doi': self.abstract_retrieval.doi,
            'scopus_id': self.abstract_retrieval.identifier,
            'authors': self.get_authors()
        }

    def get_authors(self):
        results = []
        for author in self.abstract_retrieval.authors:
            results.append({
                'first_name': author.given_name,
                'last_name': author.surname,
                'scopus_id': author.auid
            })
        return results

    def _convert_date(self, date: str):
        date_time = datetime.datetime.strptime(date, '%Y-%m-%d')
        return date_time.strftime('%Y-%m-%dT%H:%M:%S')

