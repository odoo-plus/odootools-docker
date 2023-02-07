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
