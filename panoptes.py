#!/usr/bin/env python

import click
from panoptesclient import Panoptes

@click.group()
def panoptes():
    pass

@panoptes.command()
@click.option('--id', help='Project ID', required=False, type=int)
@click.option('--display-name')
@click.argument('slug', required=False)
def project(id, display_name, slug):
    p = Panoptes('https://panoptes.zooniverse.org/api')
    projects = p.get_project(id, slug=slug, display_name=display_name)

    for proj_data in projects['projects']:
        click.echo('Project name: %s' % proj_data['display_name'])
        click.echo('\tClassification count: %s' % proj_data['classifications_count'])
        click.echo('\tSubject count: %s' % proj_data['subjects_count'])
        click.echo('')

if __name__ == '__main__':
    panoptes()
