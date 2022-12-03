from setuptools import setup, find_packages

setup(
    name='panoptescli',
    version='1.1.4',
    url='https://github.com/zooniverse/panoptes-cli',
    author='Adam McMaster / Zooniverse',
    author_email='contact@zooniverse.org',
    description=(
        'A command-line client for Panoptes, the API behind the Zooniverse'
    ),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click>=6.7,<8.2',
        'PyYAML>=5.1,<6.1',
        'panoptes-client>=1.4,<2.0',
        'humanize>=0.5.1,<4.5',
        'pathvalidate>=0.29.0,<2.6',
    ],
    entry_points='''
        [console_scripts]
        panoptes=panoptes_cli.scripts.panoptes:cli
    ''',
)
