#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="django-codestore",
    version="0.1",
    license='BSD',
    description="Edit and run python scripts in your django website ONLINE",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
