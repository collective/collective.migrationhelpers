# -*- coding: utf-8 -*-
"""Installer for the collective.migrationhelpers package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='collective.migrationhelpers',
    version='1.0a1',
    description="Helpers to use during migrations.",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Philip Bauer',
    author_email='bauer@starzel.de',
    url='https://github.com/collective/collective.migrationhelpers',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/collective.migrationhelpers',
        'Source': 'https://github.com/collective/collective.migrationhelpers',
        'Tracker': 'https://github.com/collective/collective.migrationhelpers/issues',
        # 'Documentation': 'https://collective.migrationhelpers.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'plone.api',
    ],
    extras_require={
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
