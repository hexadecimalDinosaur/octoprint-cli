#!/usr/bin/python3
import configparser
from os.path import expanduser
import os
from api import api
import sys

config = configparser.ConfigParser()
configComplete = True
configExists = False
try:
    open('config.ini')
    config.read(os.path.join(sys.path[0],'config.ini'))
    destination = config['server']['ServerAddress']
    key = config['server']['ApiKey']
    configExists = True
except KeyError:
    configComplete = False
except FileNotFoundError:
    try:
        open(expanduser('~/.config/octoprint-cli.ini'))
        config.read(expanduser('~/.config/octoprint-cli.ini'))
        destination = config['server']['ServerAddress']
        key = config['server']['ApiKey']
        configExists = True
    except KeyError:
        configComplete = False
    except FileNotFoundError:
        pass

color = True #termcolor configuration
if os.name=='nt':
    def colored(*args):
        return args[0]
    color = False
try:
    if config['preferences']['FormattedText'] == "false":
        def colored(*args, attrs=None):
            return args[0]
        color = False
except KeyError:
    pass
if color == True:
    from termcolor import colored

if configComplete == False:
    print(colored("Configuration file is not complete", 'red', attrs=['bold']))
    sys.exit(1)
if configExists == False:
    print(colored("Configuration file does not exist", 'red', attrs=['bold']))
    sys.exit(1)

if not(destination.startswith('http://') or destination.startswith('https://')): #add http if missing
    destination = "http://" + destination
if destination.endswith('/'): #remove trailing slash
    destination = destination[:-1]

caller = api(key,destination)
if caller.connectionTest() == False:
    print(colored("OctoPrint server cannot be reached", 'red', attrs=['bold']))
    sys.exit(1)
if caller.authTest() == False:
    print(colored("X-API-Key is incorrect", 'red', attrs=['bold']))
    sys.exit(1)

args = sys.argv
for i in range(len(args)):
    args[i] = args[i].lower()

try:
    if args[1] == 'version':
        data=caller.getVersionInfo()
        print("OctoPrint v" + data['server'] + " - API v" + data['api'])
        sys.exit(0)


except IndexError:
    print(colored("Not enough arguments specified", 'red', attrs=['bold']))