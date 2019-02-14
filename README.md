# Panoptes CLI

A command-line interface for [Panoptes](https://github.com/zooniverse/Panoptes),
the API behind [the Zooniverse](https://www.zooniverse.org/).

## Installation

The Panoptes CLI is written in Python, so in order to install it you will need
to install either Python 2 or Python 3, along with `pip`. macOS and Linux
already come with Python installed, so run this to see if you already have
everything you need:

```
$ python --version && pip --version
```

If you see an error like `python: command not found` or `pip: command not found`
then you will need to install this:

- [Python installation](https://wiki.python.org/moin/BeginnersGuide/Download)
- [Pip installation](https://pip.pypa.io/en/stable/installing/)

Once these are installed you can just use `pip` to install the latest release of
the CLI:

```
$ pip install panoptescli
```

Alternatively, if you want to preview the next release you can install HEAD
directly from GitHub (though be aware that this may contain
bugs/untested/incomplete features):

```
$ pip install -U git+git://github.com/zooniverse/panoptes-cli.git
```

To upgrade an existing installation to the latest version:

```
pip install -U panoptescli
```

## Built-in help

Every command comes with a built in `--help` option, which explains how to use
it.

```
$ panoptes --help
Usage: panoptes [OPTIONS] COMMAND [ARGS]...

Options:
  -e, --endpoint TEXT  Overides the default API endpoint
  -a, --admin          Enables admin mode. Ignored if you're not logged in as
                       an administrator.
  --version            Show the version and exit.
  --help               Show this message and exit.

Commands:
  configure    Sets default values for configuration...
  info         Displays version and environment information...
  project      Contains commands for managing projects.
  subject      Contains commands for retrieving information...
  subject-set  Contains commands for managing subject sets.
  workflow     Contains commands for managing workflows.
```

```
$ panoptes project --help
Usage: panoptes project [OPTIONS] COMMAND [ARGS]...

  Contains commands for managing projects.

Options:
  --help  Show this message and exit.

Commands:
  create    Creates a new project.
  download  Downloads project-level data exports.
  ls        Lists project IDs and names.
  modify    Changes the attributes of an existing...
```

```
$ panoptes subject-set upload-subjects --help
Usage: panoptes subject-set upload-subjects [OPTIONS] SUBJECT_SET_ID MANIFEST_FILES...

  Uploads subjects from each of the given MANIFEST_FILES.

  Example with only local files:

  $ panoptes subject-set upload-subjects 4667 manifest.csv

  Local filenames will be automatically detected in the manifest and
  uploaded.

  If you are hosting your media yourself, you can put the URLs in the
  manifest and specify the column number(s):

  $ panoptes subject-set upload-subjects -r 1 4667 manifest.csv

  $ panoptes subject-set upload-subjects -r 1 -r 2 4667 manifest.csv

  Any local files will still be detected and uploaded.

Options:
  -M, --allow-missing            Do not abort when creating subjects with no
                                 media files.
  -r, --remote-location INTEGER  Specify a field (by column number) in the
                                 manifest which contains a URL to a remote
                                 media location. Can be used more than once.
  -m, --mime-type TEXT           MIME type for remote media. Defaults to
                                 image/png. Has no effect without --remote-
                                 location.
  --help                         Show this message and exit.
```

## Uploading non-image media types

If you wish to upload subjects with non-image media (e.g. audio or video),
you will need to make sure you have the `libmagic` library installed. If you
don't already have `libmagic`, please see the [dependency information for
python-magic](https://github.com/ahupp/python-magic#dependencies) for more
details.

To check if `libmagic` is installed, run this command:

```
$ panoptes info
```

If you see `libmagic: False` in the output then it isn't installed.

## Command Line Examples

This readme does not list everything that the CLI can do. For a full list of
commands and their options, use the built in help as described above.

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
$ panoptes subject-set create 2797 "My first subject set"
4667 My first subject set
```

### Make your project public

```
$ panoptes project modify --public 2797
2797 zooniverse/my-project My Project
```

### Upload subjects

```
$ panoptes subject-set upload-subjects 4667 manifest.csv
```

Local filenames will be automatically detected in the manifest and uploaded. If
you are hosting your media yourself, you can put the URLs in the manifest and
specify the column number(s) and optionally set the file type if you're not
uploading PNG images:

```
$ panoptes subject-set upload-subjects -m image/jpeg -r 1 4667 manifest.csv
$ panoptes subject-set upload-subjects -r 1 -r 2 4667 manifest.csv
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
$ panoptes workflow add-subject-sets 1579 4667
```

### List subject sets in a workflow

```
$ panoptes subject-set ls -w 1579
4667 My first subject set
```

### List subject sets in a project

```
$ panoptes subject-set ls -p 2797
```

### Verify that subject set 4667 is in project 2797

```
$ panoptes subject-set ls -p 2797 4667
```

### Add known subjects to a subject set

```
# for known subjects with ids 3, 2, 1 and subject set with id 999
$ panoptes subject-set add-subjects 999 3 2 1
```
