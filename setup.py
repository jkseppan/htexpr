#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md") as f:
    readme = f.read()

requirements = ["parsimonious>=0.9.0,<0.11", "toolz>=0.9,<0.13"]
setup_requirements = ["pytest-runner"]
example_requirements = [
    "dash>=2.0.0,<2.5",
    "dash-renderer>=0.20,<2.5",
    "dash-bootstrap-components>=1.0.0,<2.0",
]
test_requirements = [
    "pytest>=6.0,<7.2",
    "pytest-cov>=2.8.1,<3.1.0",
    "pytest-sugar~=0.9.3",
    "dash[testing]>=2.0.0,<2.5",
    "dash-renderer>=0.20,<2.5",
    "dash-bootstrap-components>=1.0.0,<2.0",
    "requests>=2.23,<2.28",
]
dev_requirements = test_requirements

setup(
    author="Jouni K. Seppänen",
    author_email="jks@iki.fi",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Markup :: HTML",
        "Framework :: Dash",
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
    version="0.1.0",
    zip_safe=True,
    python_requires=">=3.7",
)
