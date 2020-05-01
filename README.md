# octoprint-cli

python3 command line tool for controlling OctoPrint servers

This tool uses the OctoPrint API to control and view the status of 3D printers connected to OctoPrint servers

This project is a work in progress. Some features may not work as intended or be missing. If you have suggestions or find bugs, please report them in issues.

## Features

* Connection status
* Print status
* Select file for print
* Pause, resume, cancel prints
* Start print
* System commands (shutdown, reboot, restart)
* Listing files
* Retrieving file/folder information

## Limitations

Currently, octoprint-cli is limited to only printers with a single extruder and bed. Support for additional extruders and chambers may be implemented in the future.

## Usage

```
octoprint-cli
================================================================================
python3 command line tool for controlling OctoPrint servers

COMMANDS
octoprint-cli help                    view this help message
octoprint-cli version                 view OctoPrint server version
octoprint-cli connection status       view printer connection status
octoprint-cli print status            view print status
octoprint-cli print start             start printing loaded file
octoprint-cli print select [file]     load file to be printed
octoprint-cli print pause             pause print
octoprint-cli print resume            resume print if paused
octoprint-cli print cancel            cancel current print
octoprint-cli system shutdown         shutdown server
octoprint-cli system reboot           reboot server
octoprint-cli system restart          restart OctoPrint server
octoprint-cli system restart-safe     restart OctoPrint server to safe mode
octoprint-cli files list              list files in the root OctoPrint directory
octoprint-cli files list [dir]        list files in directory
octoprint-cli files info [file]       find information about file or directory
```

## Screenshots

![status commands](screenshots/print-status.png)

## Dependencies

* termcolor
* requests

## Configuration

The tool reads its configuration from either `config.ini` in the script directory or from `~/.config/octoprint-cli.ini`

A sample config file has been included in `sample-config.ini`

```ini
[server]
ServerAddress = SERVER_ADDRESS_HERE
ApiKey = API_KEY_HERE
```

## Todo List

* Temperature status and setting
* Connect to printer
* Upload files
