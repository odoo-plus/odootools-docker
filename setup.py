import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="odoo_image_builder",
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    package_data={
        "odoo_image_builder": ["templates/**/*"],
    },
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'Jinja2',
    ],
    entry_points={
        'console_scripts': [
            "odoo-platform-arch=odoo_image_builder.cli.platform:main",
            "odoo-image-build=odoo_image_builder.cli.build:main",
            "odoo-image-context=odoo_image_builder.cli.context:main",
        ]
    }
)
