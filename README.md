# octoprint-cli
python3 command line tool for controlling OctoPrint servers

This tool uses the OctoPrint API to control and view the status of 3D printers connected to OctoPrint servers

This project is a work in progress. Some features may not work as intended or be missing. If you have suggestions or find bugs, please report them in issues.


## Features
* Connection status
* Print status
* Select file
* Pause, resume, cancel
* Start print


## Usage
```
octoprint-cli
======================================================================
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
* Server file listing
* Retreive file information
* Temperature status and setting
* Connect to printer
* OctoPrint power controls
* Upload files