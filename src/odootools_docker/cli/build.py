import click
from .. import renderer


@click.command()
def render():
    print(renderer.render())
    return True
