#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import setup, find_packages
from atcodertools.release_management.version import __version__

try:
    with open('README.md') as f:
        readme = f.read()
except IOError:
    readme = ''


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="atcoder-tools",
    version=__version__,
    description="Convenient modules & tools for AtCoder users, written in Python 3.5",
    url='https://github.com/kyuridenamida/atcoder-tools',
    author='kyuridenamida',
    author_email='tyotyo3@gmail.com',
    long_description=readme,
    packages=find_packages(exclude=('tests',)),
    install_requires=_requires_from_file('requirements.txt'),
    license="MIT",
    scripts=['atcoder-tools'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ]
)
