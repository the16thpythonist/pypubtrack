import os
import shutil

from pathlib import Path
from typing import Iterable, Dict, Any

PATH = Path(__file__).parent.absolute()


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


# MISC. UTILITIES
# ===============

def get_version() -> str:
    version_path = os.path.join(PATH, 'VERSION')
    with open(version_path, mode='r') as file:
        return file.read().replace('\n', '').replace(' ', '')


def author_name_kitopen(first_name: str, last_name: str) -> str:
    return '{}, {}*'.format(
        last_name.upper(),
        first_name[0].upper()
    )


