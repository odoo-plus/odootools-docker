import sys
import json


def get_context():
    """
    Parse from stdin a context formatted in JSON.
    """
    return json.load(sys.stdin)


def exit_ok(data):
    """
    Print a JSON string to stdout and exit with code 0.
    """
    print(json.dumps(data), end="")
    sys.exit(0)


def exit_err(data):
    """
    Output a JSON data to stdout and exit with an error code = 1.
    """
    print(json.dumps(data), end="")
    sys.exit(1)
