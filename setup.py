from setuptools import setup, find_packages

setup(
    name='panoptescli',
    version='1.1',
    url='https://github.com/zooniverse/panoptes-cli',
    author='Adam McMaster',
    author_email='adam@zooniverse.org',
    description=(
        'A command-line client for Panoptes, the API behind the Zooniverse'
    ),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click>=6.7,<7.1',
        'PyYAML>=3.12,<5.2',
        'panoptes-client>=1.0,<2.0',
        'humanize>=0.5.1,<0.6',
        'pathvalidate>=0.29.0,<0.30',
        'keyring>=19.2,<19.3',
    ],
    entry_points='''
        [console_scripts]
        panoptes=panoptes_cli.scripts.panoptes:cli
    ''',
)
