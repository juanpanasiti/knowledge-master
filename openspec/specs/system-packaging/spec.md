# System Packaging Specification

## Purpose

Enables global system installation, desktop launcher registration, and automated update workflow for the Knowledge Master application.

## Requirements

### Requirement: Global Command-Line Installation
The system SHALL provide an installation script `install.sh` that installs or updates the application globally using `uv tool install` into the user's environment.

#### Scenario: Running global installer
- **WHEN** the user executes `./install.sh` from the repository root
- **THEN** the application is compiled and installed into `~/.local/bin/knowledge-master`, replacing any previous version.

### Requirement: Desktop Menu Integration
The installation process SHALL register an official desktop launcher `.desktop` file and copy the custom application icon into the user's desktop icon directories.

#### Scenario: Desktop environment integration
- **WHEN** the installer completes execution
- **THEN** `~/.local/share/applications/knowledge-master.desktop` is created or refreshed with the proper icon and executable path, and `knowledge-master.png` is installed in `~/.local/share/icons/hicolor/128x128/apps/`, allowing launch and display from the OS system application menu.

### Requirement: Application Window and Web Favicon Branding
The application SHALL display the custom application branding icon as its window and browser favicon during runtime.

#### Scenario: Launching application in native or browser mode
- **WHEN** the application is started via CLI or desktop launcher
- **THEN** the native window chrome and web browser tab display the bundled custom favicon.

### Requirement: Local Development Run Mode
The application SHALL support direct local development execution without requiring global reinstallation.

#### Scenario: Running locally via uv
- **WHEN** the developer executes `uv run knowledge-master` inside the project root
- **THEN** the native desktop window opens immediately running the local working tree code.
