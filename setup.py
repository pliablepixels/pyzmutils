#!/usr/bin/python3

import io
import os
import re
import codecs

from setuptools import setup

#Package meta-data.
NAME = 'pyzmutils'
DESCRIPTION = 'ZoneMinder Base Utilities for Python'
URL = 'https://github.com/pliablepixels/pyzmutils/'
AUTHOR_EMAIL = 'pliablepixels@gmail.com'
AUTHOR = 'Pliable Pixels'
LICENSE = 'GPL'
INSTALL_REQUIRES=['psutil', 'SQLAlchemy', 'PyMySQL']


here = os.path.abspath(os.path.dirname(__file__))
# read the contents of your README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(name = NAME,
      version = find_version('pyzmutils','__init__.py'),
      description = DESCRIPTION,
      long_description = long_description,
      long_description_content_type='text/markdown',
      author = AUTHOR,
      author_email = AUTHOR_EMAIL,
      url = URL,
      license = LICENSE,
      install_requires=INSTALL_REQUIRES,
      py_modules = ['pyzmutils.logger',
                    ]
      )

