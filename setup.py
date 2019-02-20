from setuptools import setup, find_packages

setup(
    name='panoptescli',
    version='1.0.2',
    url='https://github.com/zooniverse/panoptes-cli',
    author='Adam McMaster',
    author_email='adam@zooniverse.org',
    description=(
        'A command-line client for Panoptes, the API behind the Zooniverse'
    ),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click>=6.7,<6.8',
        'PyYAML>=3.12,<4.2',
        'panoptes-client>=1.0,<2.0',
    ],
    entry_points='''
        [console_scripts]
        panoptes=panoptes_cli.scripts.panoptes:cli
    ''',
)
