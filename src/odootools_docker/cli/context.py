import toml
import click

from odoo_tools.services.objects import ServiceManifests

from argparse import ArgumentParser
from ..renderer import make_context
from ..tools import exit_ok, get_context


@click.command()
@click.option(
    '-v',
    '--version',
    help="Odoo Version"
)
@click.option(
    '--ref',
    help="Git comment referencence",
    default=""
)
@click.option(
    '--release',
    help="Odoo official release from https://github.com/odoo/odoo.git .",
    default=""
)
@click.option(
    '--repo',
    default="https://github.com/odoo/odoo.git"
)
@click.option(
    '--languages',
    default="all",
    help="Languages to keep when setting odoo as a csv value",
)
@click.option(
    '--service-file',
    help="Service file"
)
@click.option(
    '-e',
    '--env',
    help="Environment of service file to use"
)
@click.option(
    '--stdin',
    help="If set, tries to read a context from stdin",
    is_flag=True,
    default=False
)
def context(version, ref, release, repo, languages, service_file, env, stdin):
    if not release and not ref and version:
        ref = version

    if not service_file:
        base_context = {
            "odoo": {
                "version": version,
                "ref": ref,
                "repo": repo,
                "release": release,
                "languages": languages
            }
        }
    elif service_file:
        filename = service_file

        services = toml.load(filename)

        manifests = ServiceManifests.parse(services)

        service = manifests.services[env].resolved

        odoo_version = service.odoo.version

        odoo_config = service.odoo
        repo_config = odoo_config.repo

        base_context = {
            "odoo": {
                "version": odoo_version,
                "ref": repo_config.ref,
                "repo": repo_config.url or repo,
                "release": "",
                "languages": odoo_config.languages or languages
            }
        }
    elif stdin:
        base_context = get_context()

    context = make_context(base_context)

    return exit_ok(context)
