import os

from setuptools import setup, find_packages

setup(
    name='panoptescli',
    version='0.1.1',
    url='https://github.com/zooniverse/panoptes-cli',
    author='Adam McMaster',
    author_email='adam@zooniverse.org',
    description=(
        'A command-line client for Panoptes, the API behind the Zooniverse'
    ),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'PyYAML',
        'panoptes-client',
    ],
    entry_points='''
        [console_scripts]
        panoptes=panoptes_cli.scripts.panoptes:cli
    ''',
)
