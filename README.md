Odootools Docker
================

Integrate itself into odootools to generate a Dockerfile that can completely configure
a base Docker Image.

The Dockerfile is built by generating a context from certain configuration.

The context itself is simply a JSON serialized text that can be obtained
from provided utilities or anywhere that can output a JSON to stdout.

When the context is ready, it can be passed to the render function that
will load all required templates to generate the Dockerfile.

Here's a simple example to build an Odoo15 image.

    odootools docker context -v 15 | odootools docker render


Here's an example adding whtmltopdf utilities:

    odootools docker context -v 15 \
    | odootools docker wkhtmltopdf \
    | odootools docker render


Working with odootools Docker
=============================

Odootools docker is a bit more than just a script to build docker images. It
can be extended by defining your own templates that can get loaded based on the
provided context.

The external templates can be provided in the context through the key `template_dirs`.

Then the `steps` list can be used to add/remove steps in the context. Those are the main
templates that will get loaded by the Dockerfile renderer in the provided order.


For example:

    {
      "template_dirs": "/custom/templates",
      "steps": [
        "a",
        "b",
        "c",
      ]
    }


Will lookup for the template name `a.jinja`, `b.jinja`, `c.jinja` from 
`/custom/templates` first, then from the installed package `odootools_docker`.

It's possible to completely overwrite the way the context is rendered.
