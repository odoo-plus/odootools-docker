import click
from .wkhtmltopdf import wkhtmltopdf
from .context import context
from .build import render


@click.group()
def docker():
    pass


docker.add_command(wkhtmltopdf)
docker.add_command(context)
docker.add_command(render)
