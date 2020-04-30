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
    print(colored("Configuration file exists but not set up completely",'red', attrs=['bold']))
    exit(1)
except FileNotFoundError:
    try:
        open(expanduser('~/.config/octoprint-cli.ini'))
        config.read(expanduser('~/.config/octoprint-cli.ini'))
        destination = config['server']['ServerAddress']
        key = config['server']['ApiKey']
    except KeyError:
        print(colored("Configuration file exists but not set up completely",'red', attrs=['bold']))
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
    print(colored("404: Server address not found or unreachable", 'red', attrs=['bold']))
    exit(1)

try:
    if args[1].lower() == "version":
        print("OctoPrint v" + version.json()['server'] + " - API v" + version.json()['api'])
        exit(0)
    
    if args[1].lower() == "help":
        help_msg()
    
    if args[1].lower() == "connection" and args[2].lower() == "status":
        request = requests.get(destination+"/api/connection", headers=header)
        if request.status_code == 403:
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()

        if data['current']['state'] == 'Operational' or data['current']['state'] == 'Printing': #connected status
            if data['current']['state'] == 'Operational':
                print(colored("✅ Printer Operational", 'green', attrs=['bold']))
            if data['current']['state'] == 'Printing':
                print(colored("✅ Printing", 'green', attrs=['bold']))
            print(colored("Printer Profile: ", attrs=['bold']) + data['options']['printerProfiles'][0]['name'])
            print(colored("Port: ", attrs=['bold']) + data['current']['port'])
            print(colored("Baudrate: ", attrs=['bold']) + str(data['current']['baudrate']))
        elif data['current']['state'] == 'Closed': #disconnected
            print(colored("❌ Printer Disconnected", 'red', attrs=['bold']))
            print(colored("Ports: ", attrs=['bold'])+",".join(data['options']['ports']))
            print(colored("Baudrates: ", attrs=['bold'])+", ".join(list(map(str,data['options']['baudrates']))))
        elif data['current']['state'].startswith("Error"): #connection error
            print(colored("❌ Error", 'red', attrs=['bold']))
            print(colored("Error: ", attrs=['bold'])+data['current']['state'][7:])
            print(colored("Ports: ", attrs=['bold'])+",".join(data['options']['ports']))
            print(colored("Baudrates: ", attrs=['bold'])+", ".join(list(map(str,data['options']['baudrates']))))
        
        exit(0)

    if args[1].lower() == "print" and args[2].lower() == "status":
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403:
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()
        
        if data['state'] == 'Offline': #printer disconnected
            print(colored("Printer Disconnected", 'red', attrs=['bold']))
        elif data['state'].startswith('Offline'): #Offline status with error message following
            print(colored("Printer Disconnected", 'red', attrs=['bold']))
            print(data['state'])
        elif data['state'].startswith('Error'): #Error status
            print(colored("❌ Error", 'red', attrs=['bold']))
            print(colored("Error: ", attrs=['bold'])+data['state'][7:])
        else:
            request2 = requests.get(destination+"/api/printer", headers=header) #this request will not work if printer disconnected
            data2 = request2.json()
            if data['state'] == "Operational" and data['job']['file']['name'] != None: #Operational with file loaded
                print(colored("Printer Operational", 'green', attrs=['bold']))
                print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
            elif data['state'] == "Operational" and data['job']['file']['name'] == None: #Operational without file loaded
                print(colored("Printer Operational", 'green', attrs=['bold']))
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
            elif data['state'] == "Printing": #Printing status
                print(colored("Printing", 'green', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
            elif data['state'] == "Paused": #Paused status
                print(colored("Paused", 'yellow', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
            elif data['state'] == "Cancelling": #Cancelling status
                print(colored("Cancelling", 'red', attrs=['bold'])) #TODO test cancel status
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
            elif data['state'] == "Error": #Error status
                print(colored("Error", 'red', attrs=['bold']))
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
        exit(0)
    
except IndexError:
    print(colored("Not enough arguments provided", 'red'))
    exit(1)