import sys
import json


def get_context():
    return json.load(sys.stdin)


def exit_ok(data):
    print(json.dumps(data), end="")
    sys.exit(0)


def exit_err(data):
    print(json.dumps(data), end="")
    sys.exit(1)
