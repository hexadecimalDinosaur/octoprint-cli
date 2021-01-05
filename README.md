# octoprint-cli

[![version](https://img.shields.io/badge/dynamic/json?color=blue&label=version&query=tag_name&url=https%3A%2F%2Fapi.github.com%2Frepos%2Fuserblackbox%2Foctoprint-cli%2Freleases%2Flatest&style=flat-square)](https://github.com/UserBlackBox/octoprint-cli/releases/latest) [![license](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=license&query=license.key&url=https%3A%2F%2Fapi.github.com%2Frepos%2FUserBlackBox%2Foctoprint-cli&style=flat-square)](https://github.com/UserBlackBox/octoprint-cli/blob/master/LICENSE)

![icon](https://raw.githubusercontent.com/UserBlackBox/octoprint-cli/master/icon/icon.png)

Python 3 command line tool for controlling OctoPrint servers

This tool uses the OctoPrint API to control and view the status of 3D printers connected to OctoPrint servers

This project is a work in progress. Some features may not work as intended or be missing. If you have suggestions or find bugs, please report them in [issues](https://github.com/UserBlackBox/octoprint-cli/issues). Feel free to fork this repo to fix issues or to implement new features.

## Features

These are the features that have been implemented so far, more functions will be implemented in the future. Current progress on features can be found on the [project board](https://github.com/UserBlackBox/octoprint-cli/projects/1).

-   Printer connection status
-   Print job status
-   File selection
-   Pause, resume, cancel prints
-   Start print
-   System commands (shutdown, reboot, restart)
-   Listing files/folders
-   Retrieving file/folder information
-   Setting extruder and bed temperature
-   Connect and disconnect from printer
-   Continuous status output with temperature status and progress bar
-   GCODE and STL file uploads to server storage
-   Run G-code on printer from terminal
-   Layer information from OctoPrint-DisplayLayerProgress plugin if installed on server

## Limitations

Currently, octoprint-cli is limited to only printers with a single extruder and heated bed. Support for additional extruders and heated chambers may be implemented in the future. This program has been tested on OctoPi 0.17.0 on the Raspberry Pi 4 running OctoPrint 1.4.1 with a Monoprice Select Mini V2.

Colored and formatted text is not available on Windows systems due to the lack of support on cmd and powershell terminals

The program requires the API key to have all permissions to run

## Installation

octoprint-cli can be installed from PyPI using `pip`. PyPI package can be found at https://pypi.org/project/octoprint-cli/

```bash
pip install octoprint-cli
```

octoprint-cli can also be installed manually using `git` and `setup.py`

```bash
git clone https://github.com/UserBlackBox/octoprint-cli.git
cd octoprint-cli
python3 setup.py install --user
```

## Dependencies

Can be found in `requirements.txt` and installed with `pip`

-   termcolor
-   requests

## Configuration

The tool reads its configuration from either `config.ini` in the application directory or from `~/.config/octoprint-cli.ini` on Linux systems

A sample config file has been included in `sample-config.ini`

```ini
[server]
;Set OctoPrint server address and x-api-key
ServerAddress = SERVER_ADDRESS_HERE
ApiKey = API_KEY_HERE

[preferences]
;Set if the program uses colored or formatted text, this setting is turned off on windows due to cmd and powershell limitations
FormattedText = true
;Set if the program should check for updates
UpdateCheck = true

[printer]
;Set maximum temperature that printer can be set to
MaxExtruderTemp = 250
MaxBedTemp = 85
```

## Usage

<details>
<summary><b>General Commands</b></summary><br>

`octoprint-cli version` - get OctoPrint server version information

`octoprint-cli continuous` - get continuous refreshing temperature, layer, and print status

</details>

<details>
<summary><b>Print Commands</b></summary><br>

`octoprint-cli print status` - get current print job status

`octoprint-cli print select [path]` - load file on server

`octoprint-cli print start` - start print job on loaded file

`octoprint-cli print cancel` - cancel current print job

`octoprint-cli print pause` - pauses the current print job

`octoprint-cli print resume` - resumes the current print job

`octoprint-cli gcode [command]` - run GCODE command on printer

`octoprint-cli layers` - get layer information during prints from the DisplayLayerProgress plugin

</details>

<details>
<summary><b>Connection Commands</b></summary><br>

`octoprint-cli connection status` - get OctoPrint print connection information

`octoprint-cli connection connect` - connect to printer, serial port and baudrate are decided automatically unless specified with the `-b [BAUDRATE]` and `-p [PORT]` flags

`octoprint-cli connection disconnect` - disconnect from printer

</details>

<details>
<summary><b>Temperature Commands</b></summary><br>

`octoprint-cli temp status` - get current and target temperatures of extruder and bed

`octoprint-cli temp extruder [temp]` - set target temperature of extruder

`octoprint-cli temp bed [temp]` - set target temperature of print bed

</details>

<details>
<summary><b>System Commands</b></summary><br>

`octoprint-cli system restart` - restart OctoPrint server

`octoprint-cli system restart-safe` - restart OctoPrint server to safe mode

`octoprint-cli reboot` - reboot OctoPrint server

`octoprint-cli shutdown` - shutdown OctoPrint server

</details>

<details>
<summary><b>File Commands</b></summary><br>

`octoprint-cli files list` - list files on OctoPrint server, listing in folders can be done with `-p [PATH]` flag, files/folders can be filtered using the `--files` and `--folders` flags

`octoprint-cli files info [file]` - get information on file on server

`octoprint-cli files upload [file]` - upload local file to server

</details>

The `-h` or `--help` flag can bring up a help message for all commands
