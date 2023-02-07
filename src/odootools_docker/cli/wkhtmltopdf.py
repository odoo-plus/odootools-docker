import click
from ..tools import exit_ok, get_context


@click.command()
@click.option(
    '-v',
    '--version',
    default='0.12.6-1'
)
def wkhtmltopdf(version):
    context = get_context()

    if 'deb_files' not in context:
        deb_files = context['deb_files'] = []

    base_repo = "https://github.com/wkhtmltopdf/packaging/releases/download"

    url_format = (
        "{base_repo}/{version}/wkhtmltox_{version}.{os_version}_{os_arch}.deb"
    )

    url = url_format.format(
        base_repo=base_repo,
        version=version,
        os_version=context['os_version'],
        os_arch=context.get('os_arch', 'amd64')
    )

    deb_files.append({
        "url": url,
        "name": "wkhtmltox"
    })

    exit_ok(context)
