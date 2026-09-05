## MODIFIED Requirements

### Requirement: Desktop Menu Integration
The installation process SHALL register an official desktop launcher `.desktop` file and copy the custom application icon into the user's desktop icon directories.

#### Scenario: Desktop environment integration
- **WHEN** the installer completes execution
- **THEN** `~/.local/share/applications/knowledge-master.desktop` is created or refreshed with the proper icon and executable path, and `knowledge-master.png` is installed in `~/.local/share/icons/hicolor/128x128/apps/`, allowing launch and display from the OS system application menu.

## ADDED Requirements

### Requirement: Application Window and Web Favicon Branding
The application SHALL display the custom application branding icon as its window and browser favicon during runtime.

#### Scenario: Launching application in native or browser mode
- **WHEN** the application is started via CLI or desktop launcher
- **THEN** the native window chrome and web browser tab display the bundled custom favicon.
