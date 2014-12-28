#!/usr/bin/env python
from setuptools import setup, find_packages
from pip.req import parse_requirements
import os

install_requires = [str(ir.req) for ir in parse_requirements(os.path.abspath(
                    os.path.join(__file__, '..', 'requirements.txt')))]

setup(
    name='geodis',
    version='1.0',
    author='DoAT Media LTD.',
    author_email='dvirsky@gmail.com',
    url='https://github.com/doat/geodis',
    packages=find_packages(),
    install_requires=install_requires
)


