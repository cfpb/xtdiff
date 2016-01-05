#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup


setup(
    name='xtdiff',
    url='http://cfpb.github.io',
    author='CFPB',
    license='CC0',
    version=__import__('xtdiff').__version__,
    description=' '.join(__import__(
        'xtdiff'
    ).__doc__.splitlines()).strip(),

    long_description=open('README.md').read() 
            if os.path.exists('README.md') else '',

    py_modules=['xtdiff', ],
    include_package_data=True,
    install_requires=[
        'lxml',
    ],
    setup_requires=[
        'nose>=1.0'
    ],

    test_suite="test_xtdiff",
)
