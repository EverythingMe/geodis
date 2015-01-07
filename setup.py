#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='geodis',
    version='2.0.9',
    author='DoAT Media LTD.',
    author_email='opensource@everything.me',
    url='https://github.com/EverythingMe/geodis',
    scripts=['geodis/geodis'],
    packages=find_packages(),
    include_package_data = True,
    install_requires=['redis>=2.7.1', 'geohasher==0.1dev', 'upoints==0.12.2']

)


