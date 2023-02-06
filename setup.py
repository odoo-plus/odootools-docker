import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="odootools_docker",
    version="0.0.1",
    author="Loïc Faure-Lacroix",
    author_email="lamerstar@gmail.com",
    description="Odootools script to generate docker images",
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
        "odootools_docker": ["templates/**/*"],
    },
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'Jinja2',
    ],
    entry_points={
    }
)
