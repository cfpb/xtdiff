#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup


setup(
    name='xtdiff',
    url='http://cfpb.github.io',
    author='CFPB',
    license='CC0',
    version='0.1.0',
    description='This implements "Change detection in hierarchically structured information", by Sudarshan S. Chawathe, Anand Rajaraman, Hector Garcia-Molina, and Jennifer Widom.',

    long_description=open('README.md').read() 
            if os.path.exists('README.md') else '',

    py_modules=['xtdiff', ],
    include_package_data=True,
    install_requires=[
        'lxml',
        'ordered-set>=2.0.0',
    ],
    dependency_links=[
        "git+https://github.com/LuminosoInsight/ordered-set#egg=ordered-set"
    ],
    setup_requires=[
        'nose>=1.0'
    ],

    test_suite="test_xtdiff",
)
