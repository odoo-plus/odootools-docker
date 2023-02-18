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
    """
    Returns a list of native libraries to install based
    on the version of odoo required in the context.

    .. note::

        TODO should use the logic into odoo-tools instead
        of duplicating the logic of packages everywhere.

    """
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
    """
    Get the python version from the python_bin as passed in the
    context.

    Args:
      context (HashMap<str, Any>): An hashmap of JSON serializable
        values used to define a rendering context for the docker image.

    Returns:
      float: The float representation of a python version like 3.6, 3.8 etc.

    .. note::
        TODO: Change the return type to something else than float. The issue is
        that some version of python could potentially become 3.59999999 instead
        of 3.6.
    """
    python_binary = context['python_bin']
    version = python_binary.replace('python', '')
    python_version = float(version)
    return python_version


def get_odoo_version(context):
    """
    Get the version of Odoo based on the context as a float.

    Args:
      context (HashMap<str, Any>): An hashmap of JSON serializable
        values used to define a rendering context for the docker image.

    Returns:
      float: The float representation of an odoo version like 14.0, 15.1 etc

    .. note::
        TODO: Change the return type to a Version type that can be compared
        even if the version contain strings like 14.0-sass.
    """
    return float(context['odoo']['version'])


def get_python_packages(context):
    """
    Returns a list of python packages required to install odoo.

    Args:
      context (HashMap<str, Any>): An hashmap of JSON serializable
        values used to define a rendering context for the docker image.

    Returns:
        List<Str>: List of strings representing a native python package. This
        function can be merged with the native package methods. There's no
        real need to split it.
    """
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
    """
    Returns a list of RepositoryObject.

    This method can be used to return a list of prepared repositories. Package
    repositories are used to install binaries that may not be directly
    available in the main repository of the selected distribution. For example,
    you'd want to use a more modern version of the postgres client to be able
    to connect to a recent database.

    There are 2 types of object.

    Those with a key already available and one with a key url and list url.

    Returns:
        List<HashMap<str, Any>>: Returns a list of repository that can be
        prepared when installing native libraries.
    """

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
    """
    Returns a list of packages required to install Odoo.

    .. note::
        This method seems to be irrelevant as Python2 is no
        longer supported.
    """
    packages = [
        "odoo-tools",
    ]

    python_version = get_python_version(context)

    if python_version < 3:
        packages += [
            "pathlib2"
        ]

    return packages


def get_odoo_packages(context):
    """
    List of packages required to install Odoo and its dependencies.

    This method returns all the packages that are necessary to install
    Odoo and its dependencies. Those packages are also not needed to run
    Odoo. They're only needed to build dependencies.

    For that reason, packages in this list are installed before Odoo is
    installed and uninstalled right after Odoo has been installed. This
    prevent those packages to be packed into a layer and making the size
    of the docker image grow.

    Args:
      context (HashMap<str, Any>): An hashmap of JSON serializable
        values used to define a rendering context for the docker image.

    Returns:
        List<Str>: List of packages that are temporarily needed.
    """
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
    """
    Returns default environment variables to define.

    Each value in the environment variables can be formatted
    to match a value in the context.

    Args:
      context (HashMap<str, Any>): An hashmap of JSON serializable
        values used to define a rendering context for the docker image.

    Returns:
        HashMap<Str, Str>: A key/value of environment variables that
        should be defined in the image.

    """
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
    """
    Returns a default context that can be used to generate an image.

    The default context will contain everything you need to generate the
    docker image. It will have all the native libraries needed for the
    parameter provided. It will also define the steps to generate the
    docker image.

    Each steps correspond to a template in `templates/*.jinja`. Those
    templates are rendered sequentially in the order defined in the
    context. The context is also available to all the steps.

    This function can be used to generate a context and have a script
    extend it or have a script later update the values.

    For example, you can execute the script using:

    .. code:: bash

        odootools docker context | ./my_script | odootols docker render


    This will output the context from this method to a custom script
    `my_script` which can then modify the context by adding more steps or
    adding/removing packages.

    Let say you want to build an image with more dependencies without having to
    add any extra layer to a common image.
    """
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
    """
    Get the current date as formatted by Odoo releases.

    Returns:
        Str: Returns a date in the format YYYYMMDD.
    """
    FORMAT = "%Y%m%d"

    if 'CUR_DATE' in os.environ:
        CUR_DATE = os.environ['CUR_DATE']
    else:
        CUR_DATE = datetime.now().strftime(FORMAT)

    return CUR_DATE


def default_labels(context):
    """
    Returns a default list of OCI labels.

    Returns:
        HashMap<Str, Str>: Returns a list of lbales to describe the image.
    """
    create_date = get_current_date()

    description = (
        "Full featured odoo image that make odoo deployment fun and secure."
    )

    author = "Loïc Faure-Lacroix <lamerstar@gmail.com>"
    documentation = "https://github.com/odoo-plus/odootools-docker"
    url = "https://hub.docker.com/r/llacroix/odoo"
    repo = "https://github.com/odoo-plus/odootools-docker"

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
    """
    Define the host config on which Odoo will run.

    This method will select the distribution to use based on
    the version of Odoo provided in the context. This means that
    if you want to install Odoo 14 on let say Ubuntu, it will select
    the last compatible version that provides a list of package that
    works with the selected version of Odoo.

    It's not 100% correct in the sense that it might be possible
    to run odoo 12 on Ubuntu focal. But it means that unless it has
    been tested with anything else. It will use an older distribution
    if needed as some recent distribution may not have the required
    dependencies or have a broken set of dependencies.

    Returns:
        HashMap<Str, Any>: Hashmap of a host configuration.
    """
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


def render(context=None):
    """
    Main method that render a context.

    This method will generate a list of loaders based on the
    template_dirs properties defined in the context. These directories
    can be added in the context to add more steps to your docker file
    or to extend the existing steps by overshadowing them in your
    own templates.

    Returns:
        Str: A rendered Dockerfile.
    """
    if context is None:
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
