#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md") as f:
    readme = f.read()

requirements = ["parsimonious~=0.8.1", "toolz~=0.9.0"]
setup_requirements = ["pytest-runner"]
test_requirements = ["pytest", "pytest-cov"]
dev_requirements = test_requirements
example_requirements = [
    "dash~=0.39.0",
    "dash-core-components~=0.44.0",
    "dash-html-components~=0.14.0",
    "dash-renderer~=0.20.0",
    "dash-table~=3.6.0",
]

setup(
    author="Jouni K. Seppänen",
    author_email="jks@iki.fi",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    description="htexpr compiles an html string into a Python expression",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    name="htexpr",
    packages=["htexpr"],
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    extras_require={"dev": dev_requirements, "examples": example_requirements},
    url="https://github.com/jkseppan/htexpr",
    version="0.0.1",
    zip_safe=True,
    python_requires=">=3.6",
)
