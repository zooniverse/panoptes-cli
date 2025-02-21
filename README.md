# Panoptes CLI

A command-line interface for [Panoptes](https://github.com/zooniverse/Panoptes),
the API behind [the Zooniverse](https://www.zooniverse.org/).

## Installation

The Panoptes CLI is written in Python, so in order to install it you will need
to install Python 3 along with `pip`. Please note: while still compatible with
Python 2.7, we have ended support for use of the CLI with this deprecated version.
macOS and Linux already come with Python installed, so run this to see if you
already have everything you need:

```
$ python --version && pip --version
```

If you see an error like `python: command not found` or `pip: command not found`
then you will need to install this:

- [Python installation](https://wiki.python.org/moin/BeginnersGuide/Download)
  (or [Miniconda installation](https://docs.conda.io/en/latest/miniconda.html))
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
$ pip install -U git+https://github.com/zooniverse/panoptes-cli.git
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

It is also possible to generate and download workflow classification or subject set classification exports
```
$ panoptes workflow download-classifications --generate 18706 workflow-18706-classifications.csv
$ panoptes subject-set download-classifications --generate 79758 subjectset-79759-classifications.csv
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

### Retire subjects in a workflow

```
# for known subjects with ids 2001, 2001 and workflow with id 101
$ panoptes workflow retire-subjects 101 2001 2002
```

### Un-Retire subjects in a workflow

```
# for known subjects with ids 2001, 2001 and workflow with id 101
$ panoptes workflow unretire-subjects 101 2001 2002
```

### Run aggregations

```
# for running batch aggregation on workflow with id 101, user id 2001 and conditional delete flag -d
$ panoptes workflow run-aggregation 101 2001 -d
```

### Get batch aggregations

```
# for fetching existing batch aggregation on workflow with id 101
$ panoptes workflow get-batch-aggregations 101
```

### Check batch aggregation run status

```
# for checking existing batch aggregation status on workflow with id 101
$ panoptes workflow check-batch-aggregation-run-status 101
```

### Get batch aggregation links

```
# for fetching links to the run aggregation on workflow with id 101
$ panoptes workflow get-batch-aggregation-links 101
```

#### By subject sets, i.e. for all the linked subjects in a subject set

```
# for known subject sets with ids 300, 301 and workflow with id 101
panoptes workflow unretire-subject-sets 101 300 301
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

### Importing iNaturalist observations

Importing iNaturalist observations to the Zooniverse as subjects is possible via an API endpoint, which is accessible via this client.

This command initiates a background job on the Zooniverse platform to import Observations. The request will return a 200 upon success, and the import will begin as the Zooniverse and iNaturalist APIs talk to each other. Once the command is issued, the work is being done remotely and you can refresh the subject set in the project builder to check its progress. The authenticated user will receive an email when this job is completed; you don't have to keep the terminal open.

This command imports “verifiable” observations, which  according to the iNat docs means “observations with a quality_grade of either `needs_id` or `research`." Project owners and collaborators can use this CLI to send a request to begin that import process:

```
# Requires an iNaturalist taxon id and a Zooniverse subject set (both integers). This will import all observations for that taxon id.
$ panoptes inaturalist import-observations --taxon-id 46017 --subject-set-id 999999
```

Optional: include an updated_since timestamp (string) to include only observations updated after that date:

```
$ panoptes inaturalist import-observations --taxon-id 46017 --subject-set-id 999999 --updated-since 2022-12-03
```

The `--updated-since` argument is a standard ISO timestamp, such as '2022-12-03' or `2022-12-03T18:56:06+00:00'. It is passed directly to the iNat Observations v2 API as the 'updated_since' query parameter.



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
