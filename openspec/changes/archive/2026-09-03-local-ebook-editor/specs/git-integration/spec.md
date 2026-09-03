## Purpose

Provides non-blocking local Git version control for individual ebook projects with graceful degradation when Git is unavailable or unconfigured.

## ADDED Requirements

### Requirement: Non-blocking Graceful Degradation
The system SHALL detect whether the system has a functional Git installation and whether Git author name and email are configured, disabling the Git panel with an informative banner if conditions are not met.

#### Scenario: Missing Git binary or user identity
- **WHEN** the user opens an ebook on a system without Git or without `user.name`/`user.email` configured
- **THEN** the Git panel displays a disabled notice explaining the missing prerequisite while all editor and workspace features remain fully functional.

### Requirement: Repository Initialization
The system SHALL detect whether the active ebook folder contains a `.git` repository and offer a one-click initialization action.

#### Scenario: Initializing a repository
- **WHEN** the user views an unversioned ebook and clicks "Initialize Git Repository"
- **THEN** the system runs repository initialization, generates a standard `.gitignore` file, and refreshes the Git status panel.

### Requirement: Granular Staging and Unstaging
The system SHALL provide controls to inspect working tree status (`git status`) and stage or unstage changes individually or in bulk.

#### Scenario: Staging modified files
- **WHEN** the user selects files or clicks "Stage All"
- **THEN** the system adds the selected files to the Git index and updates the staged files list.

### Requirement: Discarding Unstaged Changes
The system SHALL allow users to discard changes in modified files relative to HEAD.

#### Scenario: Discarding changes on a file
- **WHEN** the user selects a modified file and confirms "Discard Changes"
- **THEN** the system reverts the file to its state at the latest commit and reloads the file in the editor if currently open.

### Requirement: Commit Creation and History Viewer
The system SHALL enable users to enter a commit message and execute commits, as well as view a reverse-chronological list of recent commits.

#### Scenario: Executing a commit
- **WHEN** the user types a commit message and clicks "Commit"
- **THEN** the system creates the commit, updates the commit log, and clears the staged files list.
