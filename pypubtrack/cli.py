"""Console script for pypubtrack."""
import sys
import os
import click
import shutil

from pykitopen import KitOpen
from pykitopen.search import YearBatching
from pykitopen.publication import Publication
from pykitopen.config import DEFAULT

from pypubtrack.util import (get_config_path,
                             get_version,
                             check_installation,
                             get_installation_path,
                             init_installation,
                             author_name_kitopen)
from pypubtrack.config import Config
from pypubtrack.pypubtrack import Pubtrack


@click.group('pypubtrack', invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Print the currently installed version of the program')
@click.option('--config', '-c', type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='Provide an alternative config file for the project')
@click.pass_context
def cli(ctx, version, config):
    """
    Command line client interface to access "pubtrack" web services.
    """
    ctx.ensure_object(dict)

    # If the "version" option was passed, the user simply wants to display the version number of the project.
    if version:
        # "get_version" loads the version string from the version file and returns it.
        version = get_version()
        click.secho('PYPUBTRACK VERSION')
        click.secho(version, bold=True)
        return 0

    # Here we need to try and load the config file. BUT if the command which was invoked is the "init" command, then
    # we dont! Because the init command creates the config file first, logically it cannot already exist then.
    if ctx.invoked_subcommand != 'init':
        # The config singleton in created. It is then loaded with the config file which was passed as an option to
        # this command. If not option was given, it attempts to load the config file from the installation folder in
        # the users home directory.
        cfg = Config()
        if config:
            cfg.load_file(config)
        else:
            # We will print an error message, if the installation folder does not exists already
            if not check_installation():
                click.secho('No valid installation folder/config file exists on this machine yet!', fg='red')
                click.secho('HINT: Run the "init" command to create a new installation folder')
                return 1

            config_path = get_config_path()
            cfg.load_file(config_path)
        # Important: The config object is then saved into the context, which is being passed to the invoked sub commands
        ctx.obj['config'] = cfg


@click.command('init', short_help='Initializes the installation folder and the config file for this project')
@click.option('--force', '-f', is_flag=True, help='Forcefully deletes any current installation before creating new one')
@click.pass_context
def init(ctx, force):
    """
    Initializes an installation folder for this CLI program in the users HOME directory. This installation folder will
    contain a config file, which can be used to store access information such as the pubtrack URL and TOKEN for future
    uses of CLI commands.
    """
    folder_path = get_installation_path()
    # If "force" flag is true, then the user wants to delete the already existing installation first.
    if force:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # "rmtree" is necessary here to delete a whole folder structure with all it's contents recursively
            shutil.rmtree(folder_path)
            click.secho('Deleted previous installation folder', fg='green')
        else:
            click.secho('No previous installation folder existed.')

    # We are being nice here and check for a potential error. If the installation folder already exists we will warn
    # the user and print a hint message
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        click.secho('An installation folder already exists for this user!', fg='red')
        click.secho('HINT: run the "init" command with the "--force" flag to delete the previous one first')
        return 1

    # "init_installation" creates the installation folder and copies the config template into it.
    init_installation()
    click.secho('Created new installation folder at "{}"'.format(folder_path), fg='green', bold=True)


@click.command('update-scopus')
def update_scopus():
    click.secho('update scopus')


@click.command('update-kitopen')
@click.option('--verbose', '-v', is_flag=True, help='Print additional console output')
@click.option('--start', '-s', type=click.STRING, default='2015', help='The year to start the KITOpen query from')
@click.pass_context
def update_kitopen(ctx, verbose, start):
    """
    Update the pubtrack records with KITOpen information.

    This commend will fetch the names of all authors from the pubtrack application. These names will be used to
    query the KITOpen database. The data from KITOpen will then finally be used to update the publication records +
    of the pubtrack application.
    """
    config = ctx.obj['config']
    pubtrack = Pubtrack(config)

    # Getting the meta authors from the pubtrack site
    click.secho('Fetching author information from pubtrack.')
    author_names = []
    meta_authors = pubtrack.meta_author.get()['results']
    for meta_author in meta_authors:
        for author in meta_author['authors']:
            # "author_name_kitopen" returns a string with the authors name. This function essentially formats the name
            # in a way so that it can be used in a query string for the KITOpen database.
            name = author_name_kitopen(author['first_name'], author['last_name'])
            author_names.append(name)
            if verbose:
                click.secho(' * Adding author "{}" to query'.format(name))

    click.secho('==> Processing total of {} authors'.format(len(author_names)))

    # Setting up KITOpen API.
    # The "view" within the kitopen config defines how many details about a single publication record are supposed to
    # be returned as a result of the query. the batching strategy defines in what kind of batches the data is supposed
    # to be returned by the database. YearBatching is generally recommended to not hit the size limit.
    kitopen_config = DEFAULT.copy()
    kitopen_config['default_view'] = Publication.VIEWS.FULL
    kitopen_config['batching_strategy'] = YearBatching

    kitopen = KitOpen(kitopen_config)

    # Using the names of these authors to query kitopen results.
    # The "author" field of the search request is supposed to be the main query string. It will combine the names of
    # all the previously fetched authors with "or" directives between them.
    click.secho('Querying KITOpen database with previously fetched authors.')
    results = kitopen.search({
        'author': ' or '.join(author_names),
        'start': start,
        'end': ''
    })

    # Processing the kitopen results to update the pubtrack entries with that
    click.secho('Updating pubtrack records with KITOpen data')
    count_total = 0
    count_success = 0
    for publication in results:
        # The "publication" results of a KITOpen request save all their content in the internal "data" dict property.
        # Here we only consider publications, which have a valid DOI as that is the only way we can properly identify
        # them and associate them with the correct entries of the pubtrack application.
        if publication.data['doi']:
            try:
                # This is what I meant. The "get_by" function attempts to fetch a publication record from the pubtrack
                # app, which is uniquely identified by the doi from the KITOpen record.
                pub = pubtrack.publication.get_by(doi=publication.data['doi'])

                # Now we need to update this record of pubtrack. For that we are going to use a http PATCH request.
                # This way we only need to assemble a dict with the actually new data.
                # The important data from KITOpen are the ID and the POF structure
                patch = {
                    'on_kitopen': True,
                    'pof_structure': publication.data['pof_structure']
                }
                if not pub['kitopen_id']:
                    patch['kitopen_id'] = publication.data['id']

                # The patch request is identified with the UUID of the publication! This is why we had to get it before
                # in the first place. The uuid is the main identifier for the pubtrack app and is different from the
                # DOI.
                pubtrack.publication.patch(pub['uuid'], patch=patch)
                count_success += 1
                if verbose:
                    click.secho(' > updated publication {}'.format(publication.data['doi']))
            except Exception as e:
                if verbose:
                    click.secho(' ! Warning updating publication {}'.format(publication.data['doi']), fg='yellow')
            finally:
                count_total += 1

    click.secho('==> Updated {}/{} publications with KITOpen data'.format(count_success, count_total),
                fg='green', bold=True)

    return 0


cli.add_command(init)
cli.add_command(update_scopus)
cli.add_command(update_kitopen)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
