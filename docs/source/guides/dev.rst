Developer Guide
===============

Writing your own script:
------------------------

This library provide a simple api to write your own python script. You can use
the functions in the `tools` module.

A basic script example can look like this:


.. code:: python

    from odootools_docker.tools import exit_ok, get_context

    # get the context
    context = get_context()

    # pass the context to stdout
    exit_ok(context)


.. note::

   It's important to understand that as the `get_context` expect data
   from stdin. As this method is also used by the provided utilities.

   It also means that your custom script cannot output anything to
   stdout. That said, it's possible to use stderr to output log messages
   as needed. Those will not get passed to piped programs.


If we wanted to override the context script, we could possibly write a script that
looks like this to predefine some configurations.


.. code:: python

    from odootools_docker.renderer import make_context
    from odootools_docker.tools import exit_ok, get_context

    base_context = {
        "odoo": {
            "version": "15.0"
        }
    }

    # get the context
    context = make_context(base_context)

    # Force the python3 with debug to be installed
    context['base_packages'] += ['python3.8-dbg']
    context['python_bin'] = 'python3.8-dbg'

    # pass the context to stdout
    exit_ok(context)


Once you have your script ready, you can also call it as such:

    ./my_script | odootools docker render


But in practice, nothing prevents you from rendering the context directly
using the `render` method.


.. code:: python

    from odootools_docker.renderer import make_context, render
    from odootools_docker.tools import exit_ok, get_context

    base_context = {
        "odoo": {
            "version": "15.0"
        }
    }

    # get the context
    context = make_context(base_context)

    # Force the python3 with debug to be installed
    context['base_packages'] += ['python3.8-dbg']
    context['python_bin'] = 'python3.8-dbg'

    print(render(context))

 
This enables you to write simple custom script to render templates
into one single script or you could write multiple scripts that can
be combined by piping the context into diffeent script transforming
the context needed to render it.

You could even have a script that fetches some context stored into
a database and then rendered. This library is trying to build a
foundation on which you can develop your customization to prepare an
unique image that completely fits your needs.
