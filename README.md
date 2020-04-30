# octoprint-cli
python3 command line tool for controlling OctoPrint servers

This tool uses the OctoPrint API to control and view the status of 3D printers connected to OctoPrint servers

This project is a work in progress. Some features may not work as intended or be missing. If you have suggestions or find bugs, please report them in issues.


## Features
* Connection status
* Print status


## Screenshots
![status commands](screenshots/Screenshot%20from%202020-04-30%2014-24-18.png)


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
* Select file to print
* Start print
* Pause, Resume, Cancel Prints
* OctoPrint power controls
* Upload files