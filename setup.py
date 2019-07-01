"""Installer for the Axonius Libs."""

__author__ = 'Axonius, Inc'

from setuptools import setup

setup(
    name='axoniussdk',
    version='1.0.0',
    description='Client for Axonius',
    author='Axonius, Inc',
    author_email='contact@axonius.com',
    url='https://www.axonius.com',
    keywords=['Axonius', 'Plugin', 'Adapter', 'IT'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 1 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['requests'],
    packages=['axoniussdk'])
