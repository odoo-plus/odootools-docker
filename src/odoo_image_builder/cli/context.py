import toml

from odoo_tools.services.objects import ServiceManifests

from argparse import ArgumentParser
from ..renderer import make_context
from ..tools import exit_ok, get_context


def get_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '-v',
        '--version',
        dest='version',
        help="Odoo Version",
    )

    parser.add_argument(
        '--ref',
        dest="ref",
        help="Git commit reference",
        default=""
    )

    parser.add_argument(
        '--release',
        dest="release",
        help="Odoo official release from https://github.com/odoo/odoo.git .",
        default=""
    )

    parser.add_argument(
        '--repo',
        dest="repo",
        default="https://github.com/odoo/odoo.git"
    )

    parser.add_argument(
        '--languages',
        dest='languages',
        default="all",
        help="Languages to keep when setting odoo as a csv value",
    )

    parser.add_argument(
        '--file',
        dest="service_file",
        help="Service file"
    )

    parser.add_argument(
        '-e',
        '--env',
        dest="env",
        help="Environment of service file to use"
    )

    parser.add_argument(
        '--stdin',
        dest="stdin",
        action="store_true",
        help="If set, tries to read a context from stdin"
    )

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if not args.release and not args.ref and args.version:
        args.ref = args.version

    if not args.service_file:
        base_context = {
            "odoo": {
                "version": args.version,
                "ref": args.ref,
                "repo": args.repo,
                "release": args.release,
                "languages": args.languages
            }
        }
    elif args.service_file:
        env = args.env
        filename = args.service_file

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
                "repo": repo_config.url or args.repo,
                "release": "",
                "languages": odoo_config.languages or args.languages
            }
        }
    elif args.stdin:
        base_context = get_context()

    context = make_context(base_context)
    context['template_dirs'] = ['template']

    return exit_ok(context)
