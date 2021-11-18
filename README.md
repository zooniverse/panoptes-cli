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
  configure    Sets default values for configuration options.
  info         Displays version and environment information for debugging.
  project      Contains commands for managing projects.
  subject      Contains commands for retrieving information about subjects.
  subject-set  Contains commands for managing subject sets.
  user         Contains commands for retrieving information about users.
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
  delete
  download  Downloads project-level data exports.
  info
  ls        Lists project IDs and names.
  modify    Changes the attributes of an existing project..
```

```
$ panoptes subject-set upload-subjects --help
Usage: panoptes subject-set upload-subjects [OPTIONS] SUBJECT_SET_ID
                                            MANIFEST_FILES...

  Uploads subjects from each of the given MANIFEST_FILES.

  Example with only local files:

  $ panoptes subject-set upload-subjects 4667 manifest.csv

  Local filenames will be automatically detected in the manifest and
  uploaded, or filename columns can be specified with --file-column.

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
                                 image/png. Can be used more than once, in
                                 which case types are mapped one to one with
                                 remote locations in the order they are given.
                                 Has no effect without --remote-location.
  -f, --file-column INTEGER      Specify a field (by column number) in the
                                 manifest which contains a local file to be
                                 uploaded. Can be used more than once.
                                 Disables auto-detection of filename columns.
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
password:
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

A manifest is a CSV file which contains the names of local media files to upload (one per column) or remote URLs (matching the `-r` option)
and any other column is recorded as subject metadata, where the column name is the key and the row/column entry is the value, for example:

file_name_1 | file_name_2 | metadata | !metadata_hidden_from_classification | #metadata_hidden_from_all
-- | -- | -- | -- | --
local_image_file_1.jpeg | local_image_file_2.jpeg | image_01 | giraffe | kenya_site_1

### Resuming a failed upload

If an upload fails for any reason, the CLI should detect the failure and give you the option of resuming the upload at a later time:

```
$ panoptes subject-set upload-subjects -m image/jpeg -r 1 4667 manifest.csv
Uploading subjects  [------------------------------------]    0%  00:41:05
Error: Upload failed.
Would you like to save the upload state to resume the upload later? [Y/n]: y
Enter filename to save to [panoptes-upload-4667.yaml]:
```

This will save a new manifest file which you can use to resume the upload. The new manifest file will be in YAML format rather than CSV, and the YAML file contains all the information about the original upload (including any command-line options you specified) along with a list of the subjects which have not yet been uploaded.

To resume the upload, simply run the `upload-subjects` command specifying the same subject set ID with the new manifest file. Note that you do not need to include any other options that you originally specified (such as `-r`, `-m`, and so on):

```
$ panoptes subject-set upload-subjects 4667 panoptes-upload-4667.yaml
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

## Debugging

To view the various requests as sent to the Panoptes API as well as other info,
include the env var `PANOPTES_DEBUG=true` before your command, like so:

`PANOPTES_DEBUG=true panoptes workflow ls -p 1234`

### Usage

1. Run `docker-compose build` to build the containers. Note there are mulitple containers for different envs, see docker-compose.yml for more details

2. Create and run all the containers with `docker-compose up`

### Testing

1. Use docker to run a testing environment bash shell and run test commands .
    1. Run `docker-compose run --rm dev sh` to start an interactive shell in the container
    1. Run `python -m unittest discover` to run the full test suite
