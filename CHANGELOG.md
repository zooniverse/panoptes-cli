## 0.5 (2017-03-22)

- New: Make `project ls` perform a full-text search
- New: Allow listing subjects in a subject set
- New: Subject to subject set linking
- New: Add commands to activate/deactivate workflows
- New: Add command to download workflow classifications exports
- Fix: Use os.path.expanduser to find config directory

## 0.4 (2017-03-13)

- New: Listing subject sets by project ID and workflow ID
- New: Listing workflows
- New: Adding and removing subject sets to and from workflows
- New: Allow uploading multiple manifests at once (changes arguments for
  `subject_set upload_subjects`)
- Increase default timeout for exports to 1 hour

## 0.3 (2016-11-21)

- New: Add all data exports
- New: Add --allow-missing option to upload_subjects
- Fix: JPEG uploading
- Fix: Open manifest file with universal newline mode
- Fix: Don't create subjects with no images

## 0.2 (2016-09-02)

- New: Project classification exports
- New: Subject retirement
- New: Add --launch-approved option to project ls
- Fix: Update `SubjectSet.add_subjects` -> `SubjectSet.add`

## 0.1 (2016-06-17)

- Initial release
- Allows creating and modifying projects and subject sets
- Allows uploading subjects to subject sets
