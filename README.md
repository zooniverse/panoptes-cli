# Panoptes CLI

A command-line interface for [Panoptes](https://github.com/zooniverse/Panoptes),
the API behind [the Zooniverse](https://www.zooniverse.org/).

## Installation

In most cases, you can just use `pip` to install the latest release:

```
$ pip install panoptescli
```

Alternatively, if you want to preview the next release you can install HEAD
directly from GitHub (though be aware that this may contain
bugs/untested/incomplete features):

```
$ pip install git+git://github.com/zooniverse/panoptes-cli.git
```

## Command Line Examples

This readme does not list everything that the CLI can do. For a full list of
commands and their options, use the built in help. E.g.:

```
$ panoptes --help
$ panoptes project --help
$ panoptes subject_set upload_subjects --help
```

### Log in and optionally set the API endpoint

```
$ panoptes configure
username []:
password []:
endpoint [https://www.zooniverse.org]:
```

Press enter without typing anything to keep the current value (shown in
brackets). You probably don't need to change the endpoint, unless you're running
your own copy of the Panoptes API.

### Create a new project

```
$ panoptes project create "My Project" "This is a description of my project"
*2797 zooniverse/my-project My Project
```

The `*` before the project ID indicates that the project is private.

### Create a subject set in your new project

```
$ panoptes subject_set create 2797 "My first subject set"
4667 My first subject set
```

### Make your project public

```
$ panoptes project modify --public 2797
2797 zooniverse/my-project My Project
```

### Upload subjects

```
$ panoptes subject_set upload_subjects 4667 manifest.csv
```

Local filenames will be automatically detected in the manifest and uploaded. If
you are hosting your media yourself, you can put the URLs in the manifest and
specify the column number(s) and optionally set the file type if you're not
uploading PNG images:

```
$ panoptes subject_set upload_subjects -m image/jpeg -r 1 4667 manifest.csv
$ panoptes subject_set upload_subjects -r 1 -r 2 4667 manifest.csv
```

### Generate and download a classifications export

```
$ panoptes project download --generate 2797 classifications.csv
```

### Generate and download a talk comments export

```
$ panoptes project download --generate --data-type talk_comments 2797 classifications.csv
```

### List workflows in your project

```
$ panoptes workflow ls -p 2797
1579 Example workflow 1
2251 Example workflow 2
```

### Add a subject set to a workflow

```
$ panoptes workflow add_subject_sets 1579 4667
```

### List subject sets in a workflow

```
$ panoptes subject_set ls -w 1579
4667 My first subject set
```

### List subject sets in a project

```
$ panoptes subject_set ls -p 2797
```

### Verify that subject set 4667 is in project 2797

```
$ panoptes subject_set ls -p 2797 4667
```
