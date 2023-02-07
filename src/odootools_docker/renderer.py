import os
from datetime import datetime
from jinja2 import (
    Environment,
    PackageLoader,
    ChoiceLoader,
    select_autoescape,
    FileSystemLoader,
)
from .tools import get_context


def get_base_packages(context):
    packages = [
        "curl",
        "libpq-dev",
        "libsasl2-2",
        "libldap-2.4-2",
        "libxml2",
        "libxmlsec1",
        "libxslt1.1",
        "sudo",
        "node-less",
        "gnupg",
        "ca-certificates",
    ]

    odoo_version = get_odoo_version(context)

    if odoo_version < 11:
        packages += [
            "ruby-sass",
            "libjpeg-dev"
        ]

    return packages


def get_python_version(context):
    python_binary = context['python_bin']
    version = python_binary.replace('python', '')
    python_version = float(version)
    return python_version


def get_odoo_version(context):
    return float(context['odoo']['version'])


def get_python_packages(context):
    python_binary = context['python_bin']

    packages = [
        python_binary
    ]

    python_version = get_python_version(context)

    if python_version >= 3:
        packages += [
            "python3-wheel",
            "python3-setuptools",
            "python3-pip",
            "python3-cryptography"
        ]
    else:
        packages += [
            "python-wheel",
            "python-setuptools",
            "python-pip",
            "python-cryptography",
            "libpython2.7"
        ]

    return packages


def get_setup_steps(context):

    steps = [
        "setup_env",
        "setup_base_dependencies",
        # "setup_repos",
        # "setup_postgres",
        "setup_odoo",
        "prepare_user",
        "setup_labels",
        "setup_command",
    ]

    return steps


def get_extra_deb_repos(context):

    odbc_repo = { # noqa
        "name": "{os_version}-microsoft",
        "key_url": "https://packages.microsoft.com/keys/microsoft.asc",
        "list_url": (
            "https://packages.microsoft.com/config/"
            "{os_name}/{os_release}/prod.list"
        ),
        "environments": {
            "ACCEPT_EULA": "Y"
        },
        "packages": [
            "msodbcsql18"
        ]
    }

    postgres_repo = {
        "url": "https://apt.postgresql.org/pub/repos/apt/",
        "name": "{os_version}-pgdg",
        "repo": "main",
        "key": "B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8",
        "packages": [
            "postgresql-client"
        ],
    }

    deb_repos = []
    deb_repos.append(postgres_repo)
    # deb_repos.append(odbc_repo)

    return [
        {
            key: value.format(**context) if isinstance(value, str) else value
            for key, value in config.items()
        }
        for config in deb_repos
    ]


def get_odoo_pip_packages(context):
    packages = [
        # "odoo-tools",
    ]

    python_version = get_python_version(context)

    if python_version < 3:
        packages += [
            "pathlib2"
        ]

    return packages


def get_odoo_packages(context):
    packages = [
        "build-essential",
        "libsasl2-dev",
        "libldap2-dev",
        "libxml2-dev",
        "libxmlsec1-dev",
        "libxslt1-dev",
        "git",
        "{python_bin}-dev".format(**context)
    ]
    return packages


def get_default_environment(context):
    envs = {
        "ODOO_RC": "/etc/odoo/odoo.conf",
        "DEPLOYMENT_AREA": "undefined",
        "LANG": "C.UTF-8",
        "PATH": "/var/lib/odoo/.local/bin:/usr/local/bin:$PATH",
        "ODOO_VERSION": "{odoo[version]}",
        "ODOO_RELEASE": "{odoo[release]}",
    }

    return {
        key: value.format(**context)
        for key, value in envs.items()
    }


def make_context(override_context=None):
    if override_context is None:
        override_context = {}

    context = {
        # "base_image": "ubuntu:22.04",
        "deb_repos": [
        ],
        "user": {
            "gid": "1000",
            "uid": "1000"
        }
    }

    context.update(override_context)
    context.update(get_host_config(context))

    deb_repos = get_extra_deb_repos(context)

    context['deb_repos'] = deb_repos
    context['base_packages'] = get_base_packages(context)
    context['base_packages'] += get_python_packages(context)
    context['steps'] = get_setup_steps(context)
    context['odoo_pip_packages'] = get_odoo_pip_packages(context)
    context['odoo_packages'] = get_odoo_packages(context)
    context['labels'] = default_labels(context)
    context['environments'] = get_default_environment(context)

    return context


def get_current_date():
    FORMAT = "%Y%m%d"

    if 'CUR_DATE' in os.environ:
        CUR_DATE = os.environ['CUR_DATE']
    else:
        CUR_DATE = datetime.now().strftime(FORMAT)

    return CUR_DATE


def default_labels(context):
    create_date = get_current_date()

    description = (
        "Full featured odoo image that make odoo deployment fun and secure."
    )

    author = "Loïc Faure-Lacroix <lamerstar@gmail.com>"
    documentation = "https://github.com/llacroix/odoo-docker"
    url = "https://hub.docker.com/r/llacroix/odoo"
    repo = "https://github.com/llacroix/odoo-docker"

    labels = {
        "org.opencontainers.image.created": create_date,
        "org.opencontainers.image.url": url,
        "org.opencontainers.image.authors": author,
        "org.opencontainers.image.documentation": documentation,
        "org.opencontainers.image.source": repo,
        "org.opencontainers.image.version": "{odoo[version]}",
        "org.opencontainers.image.vendor": "LLacroix",
        "org.opencontainers.image.ref.name": "{odoo[ref]}",
        "org.opencontainers.image.title": "Odoo {odoo[version]}",
        "org.opencontainers.image.description": description
    }

    return {
        key: value.format(**context)
        for key, value in labels.items()
    }


def get_host_config(context):
    odoo_version = get_odoo_version(context)
    os_name = "ubuntu"

    if odoo_version <= 12:
        os_version = "bionic"
        os_release = "18.04"
    elif odoo_version <= 15:
        os_version = "focal"
        os_release = "20.04"
    # elif odoo_version <= 15:
    #     os_version = "foca"
    #     os_release = "22.04"

    if odoo_version <= 10:
        python_bin = "python2.7"
    elif odoo_version <= 12:
        python_bin = "python3.6"
    elif odoo_version <= 15:
        python_bin = "python3.8"

    return {
        "python_bin": python_bin,
        "os_name": os_name,
        "os_version": os_version,
        "os_release": os_release,
        "os_arch": "amd64"
    }


def render():
    context = get_context()

    loaders = [
        FileSystemLoader(dirname)
        for dirname in context.get('template_dirs', [])
    ]

    loaders.append(
        PackageLoader("odootools_docker", "templates")
    )

    loader = ChoiceLoader(loaders)

    env = Environment(
        loader=loader,
        autoescape=select_autoescape()
    )

    template = env.get_template("main.jinja")
    return template.render(**context)
