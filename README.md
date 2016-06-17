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
$ panoptes subject_set upload_subjects --subject-set-id 4667 --manifest-file manifest.csv
```
