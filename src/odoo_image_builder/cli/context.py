import toml

from odoo_tools.configuration.services import get_services, Normalizer

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

        ignore_self = True

        normalizer = Normalizer(
            inherit_addons=True,
            resolve_inheritance=True,
            self_url=None,
            ignore_self=ignore_self
        )

        services = normalizer.parse(services)
        by_name = get_services(services)
        service = by_name.get(env)

        odoo_version = service['odoo_version']

        odoo_config = service.get('odoo', {})
        repo_config = odoo_config.get('repo', {})

        base_context = {
            "odoo": {
                "version": odoo_version,
                "ref": repo_config.get('commit', odoo_version),
                "repo": repo_config.get('url') or args.repo,
                "release": "",
                "languages": odoo_config.get('languages') or args.languages
            }
        }
    elif args.stdin:
        base_context = get_context()

    context = make_context(base_context)
    return exit_ok(context)
