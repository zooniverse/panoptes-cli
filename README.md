# Panoptes CLI

A command-line interface for [Panoptes](https://github.com/zooniverse/Panoptes),
the API behind [the Zooniverse](https://www.zooniverse.org/).

## Installation

Install directly from GitHub:

```
$ pip install git+git://github.com/zooniverse/panoptes-cli.git
```

## Command Line Examples

Print all projects:

```
panoptes project ls
```

## Python Module Examples

Print all projects:

```
from panoptes_client import Project

for project in Project.find():
    print project
```
