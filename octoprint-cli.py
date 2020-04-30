#!/usr/bin/python3
import requests
import sys
import configparser
import json
from os.path import expanduser
import os
import datetime

if os.name=='nt':
    def cprint(*args):
        print(args[0])
    def colored(*args):
        return args[0]
else:
    from termcolor import colored


args = sys.argv

def help_msg():
    name = args[0]
    print("octoprint-cli")
    print("======================================================================")
    print("python3 command line tool for controlling OctoPrint servers")
    print()
    print("COMMANDS")
    print(name+" help                    view this help message")
    print(name+" version                 view OctoPrint server version")
    print(name+" connection status       view printer connection status")
    print(name+" print status            view print status")
    exit(0)

if "-h" in args or "--help" in args:
    help_msg()

config = configparser.ConfigParser()
try:
    open('config.ini')
    config.read('config.ini')
    destination = config['server']['ServerAddress']
    key = config['server']['ApiKey']
except KeyError:
    print(colored("Configuration file exists but not set up completely",'red'))
    exit(1)
except FileNotFoundError:
    try:
        open(expanduser('~/.config/octoprint-cli.ini'))
        config.read(expanduser('~/.config/octoprint-cli.ini'))
        destination = config['server']['ServerAddress']
        key = config['server']['ApiKey']
    except KeyError:
        print(colored("Configuration file exists but not set up completely",'red'))
        exit(1)
    except FileNotFoundError:
        print("No config file exists")
        exit(1)

if not(destination.startswith('http://') or destination.startswith('https://')):
    destination = "http://" + destination
if destination.endswith('/'):
    destination = destination[:-1]

header = {'Content-Type': 'application/json', 'X-API-Key':key}

version = requests.get(destination+"/api/version", headers=header)
if version.status_code == 404:
    print("404: Server address not found")
    exit(1)

try:
    if args[1].lower() == "version":
        print("OctoPrint v" + version.json()['server'] + " - API v" + version.json()['api'])
        exit(0)
    
    if args[1].lower() == "help":
        help_msg()
    
    if args[1].lower() == "connection" and args[2].lower() == "status":
        request = requests.get("http://192.168.2.99/api/connection", headers=header)
        if version.status_code == 404:
            print("404: Server address not found")
            exit(1)
        if version.status_code == 403:
            print("403: Authentication fail")
            exit(1)
        data = request.json()

        if data['current']['state'] == 'Operational' or data['current']['state'] == 'Printing':
            if data['current']['state'] == 'Operational':
                print(colored("✅ Printer Operational", 'green', attrs=['bold']))
            if data['current']['state'] == 'Printing':
                print(colored("✅ Printing", 'green', attrs=['bold']))
            print(colored("Printer: ", 'white', attrs=['bold']) + data['options']['printerProfiles'][0]['name'])
            print(colored("Port: ", 'white', attrs=['bold']) + data['current']['port'])
            print(colored("Baudrate: ", 'white', attrs=['bold']) + str(data['current']['baudrate']))
        
        exit(0)

    if args[1].lower() == "print" and args[2].lower() == "status":
        request = requests.get("http://192.168.2.99/api/job", headers=header)
        data = request.json()
        request2 = requests.get("http://192.168.2.99/api/printer", headers=header)
        data2 = request2.json()
        if data['state'] == "Operational":
            print(colored("Printer Operational", 'green', attrs=['bold']))
            print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
            print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
            print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
            print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
        elif data['state'] == "Printing":
            print(colored("Printing", 'green', attrs=['bold']))
            print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
            print(colored("Estimated Total Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
            print(colored("Estimated Print Time Left: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
            print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
            print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
            print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
        elif data['state'] == "Paused":
            print(colored("Paused", 'yellow', attrs=['bold']))
            print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
            print(colored("Estimated Total Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
            print(colored("Estimated Print Time Left: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
            print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
            print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
            print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
        elif data['state'] == "Cancelling":
            print(colored("Cancelling", 'red', attrs=['bold']))
            print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
            print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
        elif data['state'] == "Error":
            print(colored("Error", 'red', attrs=['bold']))
            print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
            print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
    
except IndexError:
    print(colored("Not enough arguments provided", 'red'))
    exit(1)