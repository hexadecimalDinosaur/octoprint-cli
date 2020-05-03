# octoprint-cli

![icon](icon/icon.png)

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
* Setting extruder and bed temperature
* Connect and disconnect from printer
* Continuous status output with temperature status and progress bar

## Limitations

Currently, octoprint-cli is limited to only printers with a single extruder and bed. Support for additional extruders and chambers may be implemented in the future. This program has been tested on OctoPi 0.17.0 on the Raspberry Pi 4 running OctoPrint 1.4.0 with a Monoprice Select Mini V2.

Colored and formatted text is not available on Windows systems due to the lack of support on cmd and powershell terminals

## Installation

Windows users can grab the application from [releases](https://github.com/UserBlackBox/octoprint-cli/releases)

Linux users can drop the python program in their user bin folder

## Dependencies

Can be found in `requirements.txt`
* termcolor
* requests

## Configuration

The tool reads its configuration from either `config.ini` in the script directory or from `~/.config/octoprint-cli.ini`

A sample config file has been included in `sample-config.ini`

```ini
[server]
;Set OctoPrint server address and x-api-key
ServerAddress = SERVER_ADDRESS_HERE
ApiKey = API_KEY_HERE

[preferences]
;Set if the program uses colored or formatted text, this setting is turned off on windows due to cmd and powershell limitations
FormattedText = true

[printer]
;Set maximum temperature that printer can be set too
MaxExtruderTemp = 250
MaxBedTemp = 85
```

## Usage

```
octoprint-cli
===============================================================================
command line tool to control octoprint servers

COMMANDS
octoprint-cli help                      view this help message
octoprint-cli print status              view job status
octoprint-cli print select [file]       load file
octoprint-cli print start               start print
octoprint-cli print pause               pause print
octoprint-cli print resume              resume print
octoprint-cli print cancel              cancel print
octoprint-cli connection status         view connection status
octoprint-cli connection connect        connect to printer with autodetection
octoprint-cli connection disconnect     connect to printer with manual settings
octoprint-cli temp status               view printer temperature status
octoprint-cli temp extruder [target]    set extruder target temperature
octoprint-cli temp bed [target]         set bed target temperature
octoprint-cli files list                list files and folders in root dir
octoprint-cli files list [dir]          list files in directory
octoprint-cli files info [name]         get information on file or folder
octoprint-cli system restart            restart OctoPrint server
octoprint-cli system restart-safe       restart OctoPrint server to safe mode
octoprint-cli system reboot             reboot server
octoprint-cli system shutdown           shutdown server
octoprint-cli continuous                get refreshing continuous status
```

## Todo List

* Upload files
