# Panoptes CLI

A command-line interface for [Panoptes](https://github.com/zooniverse/Panoptes),
the API behind [the Zooniverse](https://www.zooniverse.org/).

## Installation

Install latest release:

```
$ pip install panoptescli
```

Install HEAD directly from GitHub:

```
$ pip install git+git://github.com/zooniverse/panoptes-cli.git
```

## Command Line Examples

Log in and optionally set the API endpoint:

```
$ panoptes configure
username []:
password []:
endpoint [https://panoptes.zooniverse.org]:
```

Press enter without typing anything to keep the current value (shown in
brackets).

Create a new project:

```
$ panoptes project create --display-name "My Project" --description "This is my project"
*2797 zooniverse/my-project My Project
```

The `*` before the project ID indicates that the project is private.

Create a subject set in your new project:

```
$ panoptes subject_set create --project-id 2797 --display-name "My first subject set"
4667 My first subject set
```

Make your project public:

```
$ panoptes project modify --project-id 2797 --public
2797 zooniverse/my-project My Project
```

Upload subjects:

```
$ panoptes subject_set upload_subjects 4667 manifest.csv
```

(Note: it's best to upload in batches of 500-1000)

Generate and download a classifications export:

```
$ panoptes project download --project-id 2797 --generate --output classifications.csv
```

Generate and download a talk comments export:

```
$ panoptes project download --project-id 2797 --generate --data-type talk_comments --output classifications.csv
```

List workflows in your project:

```
$ panoptes workflow ls --project-id 2797
1579 Example workflow 1
2251 Example workflow 2
```

Add a subject set to a workflow:

```
$ panoptes workflow add_subject_sets 1579 4667
```

List subject sets in a workflow:

```
$ panoptes subject_set ls --workflow-id 1579
4667 My first subject set
```
