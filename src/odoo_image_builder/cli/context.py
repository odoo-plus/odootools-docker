from ..renderer import make_context
from ..tools import exit_ok, get_context


def main():
    parent_context = get_context()
    context = make_context(parent_context)
    return exit_ok(context)
