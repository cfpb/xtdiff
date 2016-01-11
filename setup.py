#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup


setup(
    name='xtdiff',
    url='https://github.com/cfpb/xtdiff',
    download_url='https://github.com/cfpb/xtdiff/archive/0.1.0.tar.gz',
    author='CFPB',
    author_email='tech@cfpb.gov',
    license='CC0',
    version='0.1.0',
    description='This implements "Change detection in hierarchically structured information", by Sudarshan S. Chawathe, Anand Rajaraman, Hector Garcia-Molina, and Jennifer Widom.',

    long_description=open('README.md').read() 
            if os.path.exists('README.md') else '',

    packages=['xtdiff', ],
    include_package_data=True,
    install_requires=[
        'lxml',
    ],
    setup_requires=[
        'nose>=1.0'
    ],

    test_suite='xtdiff.tests',
)
