#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import logging
import os
import sys

from setuptools import find_packages, setup


sys.path.append(
    os.path.join(os.path.dirname(__file__), 'src')
)

# noqa
from barbequeue import __version__  # isort:skip  # noqa


def read_file(fname):
    """
    Read file and decode in py2k
    """
    if sys.version_info < (3,):
        return open(fname).read().decode("utf-8")
    return open(fname).read()


dist_name = 'barbequeue'

readme = "Empty for now."  # read_file('README.rst')

# Default description of the distributed package
description = ("""A queueing library with support for Windows and Unix.""")


######################################
# STATIC AND DYNAMIC BUILD SPECIFICS #
######################################


def enable_log_to_stdout(logname):
    """Given a log name, outputs > INFO to stdout."""
    log = logging.getLogger(logname)
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    log.addHandler(ch)


setup(
    name=dist_name,
    version=__version__,
    description=description,
    long_description="{readme}".format(readme=readme),
    author='Learning Equality',
    author_email='aron+barbequeue@learningequality.org',
    url='https://github.com/learningequality/barbequeue',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    keywords=('queue', 'async'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
