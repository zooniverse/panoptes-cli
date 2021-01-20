from setuptools import setup, find_packages

setup(
    name='panoptescli',
    version='1.1.3',
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
        'PyYAML>=5.1,<5.5',
        'panoptes-client>=1.3,<2.0',
        'humanize>=0.5.1,<1.1',
        'pathvalidate>=0.29.0,<0.30',
    ],
    entry_points='''
        [console_scripts]
        panoptes=panoptes_cli.scripts.panoptes:cli
    ''',
)
