#!/usr/bin/python3
#Created by Ivy Fan-Chiang
#This program is licensed under the MIT License, details at https://github.com/UserBlackBox/octoprint-cli/blob/master/LICENSE
#Details about this program and usage at https://github.com/UserBlackBox/octoprint-cli/blob/master/README.md
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

def help_msg(): #help message
    name = args[0]
    print("octoprint-cli")
    print("================================================================================")
    print("python3 command line tool for controlling OctoPrint servers")
    print()
    print("COMMANDS")
    print(name+" help                    view this help message")
    print(name+" version                 view OctoPrint server version")
    print(name+" connection status       view printer connection status")
    print(name+" print status            view print status")
    print(name+" print start             start printing loaded file")
    print(name+" print select [file]     load file to be printed")
    print(name+" print pause             pause print")
    print(name+" print resume            resume print if paused")
    print(name+" print cancel            cancel current print")
    print(name+" system shutdown         shutdown server")
    print(name+" system reboot           reboot server")
    print(name+" system restart          restart OctoPrint server")
    print(name+" system restart-safe     restart OctoPrint server to safe mode")
    print(name+" files list              list files in the root OctoPrint directory")
    print(name+" files list [dir]        list files in directory")
    print(name+" files info [file]       find information about file or directory")
    print(name+" temp status             find printer temperature information")
    print(name+" temp extruder [temp]    set extruder temperature")
    print(name+" temp bed [temp]         set bed temperature")
    exit(0)

if "-h" in args or "--help" in args:
    help_msg()

config = configparser.ConfigParser() #load config file
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

try:
    if not config['printer']['MaxExtruderTemp'].isdigit():
        print(colored("printer/MaxExtruderTemp in configuration file is not an integer value", 'red', attrs=['bold']))
        exit(1)
    if not config['printer']['MaxBedTemp'].isdigit():
        print(colored("printer/MaxBedTemp in configuration file is not an integer value", 'red', attrs=['bold']))
        exit(1)
except KeyError:
    pass

if not(destination.startswith('http://') or destination.startswith('https://')): #add http if missing
    destination = "http://" + destination
if destination.endswith('/'): #remove trailing slash
    destination = destination[:-1]

header = {'Content-Type': 'application/json', 'X-API-Key':key}

version = requests.get(destination+"/api/version", headers=header) #test if server reachable
if version.status_code == 404:
    print(colored("404: Server address not found or unreachable", 'red', attrs=['bold']))
    exit(1)

try:
    if args[1].lower() == "version": #version
        print("OctoPrint v" + version.json()['server'] + " - API v" + version.json()['api'])
        exit(0)
    
    if args[1].lower() == "help": #help
        help_msg()
    
    if args[1].lower() == "connection" and args[2].lower() == "status": #connection status
        request = requests.get(destination+"/api/connection", headers=header)
        if request.status_code == 403: #authentication test
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

    if args[1].lower() == "print" and args[2].lower() == "status": #print status
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403: #authentication test
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
            elif data['state'] == "Pausing": #Paused status
                print(colored("Pausing", 'yellow', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
            elif data['state'] == "Cancelling": #Cancelling status
                print(colored("Cancelling", 'red', attrs=['bold']))
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
            elif data['state'] == "Error": #Error status
                print(colored("Error", 'red', attrs=['bold']))
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
        exit(0)

    if args[1].lower() == "print" and args[2].lower() == "start": #print start
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403: #authentication test
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()
        if data['job']['file']['name'] == None: #if no file has been selected for printing don't bother
            print("No file has been selected for printing")
            exit(1)
        elif data['state'] != "Operational": #if not idle don't bother
            if data['state'] == "Printing": #if already printing don't bother
                print(colored("Printer is already running a print job", 'red', attrs=['bold']))
                print("Try running '"+args[0]+" print status' for more details")
            else: #if some other state something is wrong
                print(colored("Printer cannot be reached", 'red', attrs=['bold']))
            exit(1)
        else:
            request = requests.post(destination+"/api/job", headers=header, data=json.dumps({"command":"start"})) #make POST start request
            if request.status_code == 409:
                print(colored("409: Server conflict", 'red', attrs=['bold']))
                exit(1)
        exit(0)
    
    if args[1].lower() == "print" and args[2].lower() == "select": #print select
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403: #authentication test
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()
        if data['state'] != "Operational": #if printer is not idle don't bother
            if data['state'] == "Printing": #if already printing prompt
                print(colored("Printer is already running a print job", 'red', attrs=['bold']))
                print("Try running '"+args[0]+" print status' for more details")
            else:
                print(colored("Printer cannot be reached", 'red', attrs=['bold']))
            exit(1)
        else:
            try: #remove leading slash
                if args[3].startswith("/"):
                    args[3] = args[3][1:]
            except IndexError:
                print(colored("Not enough arguments provided: file not specified", 'red', attrs=['bold']))
                exit(1)
            request = requests.post(destination+"/api/files/local/"+args[3], headers=header, data=json.dumps({"command":"select"}))
            if request.status_code == 409: #error codes
                print(colored("409: Server conflict", 'red', attrs=['bold']))
                exit(1)
            if request.status_code == 400:
                print(colored("File does not exist", 'red', attrs=['bold']))
                print("If the file exists you may be missing the full path")
                exit(1)
            if request.status_code != 204:
                print(colored("File selection failed", 'red', attrs=['bold']))
                exit(1)
            else: #show success
                print(args[3]+" selected")
        exit(0)
    
    if args[1].lower() == "print" and args[2].lower() == "pause": #print pause
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403: #authentication test
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()

        if data['state'] == "Operational": #if not printing don't bother
            print(colored("Printer is not printing", 'red', attrs=['bold']))
            print("Try running '"+args[0]+" print status' for more details")
        elif data['state'] == "Paused": #if already paused don't bother
            print(colored("Printer is already paused", 'red', attrs=['bold']))
            exit(0)
        elif data['state'] != "Printing": #if some other state something is wrong
            print(colored("Printer cannot be reached", 'red', attrs=['bold']))
            exit(1)
        else:
            request = requests.post(destination+"/api/job", headers=header, data=json.dumps({"command":"pause", "action":"pause"}))
            if request.status_code == 409:
                print(colored("409: Server conflict", 'red', attrs=['bold']))
                exit(1)
        exit(0)

    if args[1].lower() == "print" and args[2].lower() == "resume": #print resume
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403: #authentication test
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()

        if data['state'] == "Operational": #if not printing don't bother
            print(colored("Printer is not printing", 'red', attrs=['bold']))
            print("Try running '"+args[0]+" print status' for more details")
            exit(1)
        elif data['state'] == "Printing": #if not paused don't bother
            print(colored("Printer is not paused", 'red', attrs=['bold']))
            exit(1)
        elif data['state'] != "Paused": #if other state something is wrong
            print(colored("Printer cannot be reached", 'red', attrs=['bold']))
            exit(1)
        else:
            request = requests.post(destination+"/api/job", headers=header, data=json.dumps({"command":"pause", "action":"resume"})) #resume request
            if request.status_code == 409:
                print(colored("409: Server conflict", 'red', attrs=['bold']))
                exit(1)
        exit(0)

    if args[1].lower() == "print" and args[2].lower() == "cancel": #print cancel
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403:
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()

        if data['state'] == "Operational": #if nothing printing don't bother
            print(colored("Printer is not printing", 'red', attrs=['bold']))
            print("Try running '"+args[0]+" print status' for more details")
            exit(1)
        elif data['state'] != "Printing": #if other status something is wrong
            print(colored("Printer cannot be reached", 'red', attrs=['bold']))
            exit(1)
        else:
            request = requests.post(destination+"/api/job", headers=header, data=json.dumps({"command":"cancel"})) #cancel request
            if request.status_code == 409:
                print(colored("409: Server conflict", 'red', attrs=['bold']))
                exit(1)
        exit(0)

    if args[1].lower() == "system": #system commands
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403: #authentication test
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()

        if data['state'] in ("Printing", "Pausing", "Paused"): #stop system commands from running if in printing state
            print(colored("The printer is currently printing, please cancel the operation before trying again", 'red', attrs=['bold']))
            exit(1)

        if args[2].lower() == "shutdown": #system shutdown
            prompt = input("You are shutting down the system. Are you sure you wish to continue? [Y/n]: ") #prompt for confirmation
            if not(prompt.lower() == "y" or prompt.lower == "yes"):
                exit(0)
            request = requests.post(destination+"/api/system/commands/core/shutdown", headers=header) #make POST request
            if request.status_code != 204: #see if successful
                print(colored("Shutdown Failed", 'red', attrs=['bold']))
            else:
                print("Shutdown Initialized")
        elif args[2].lower() == "reboot": #system reboot
            prompt = input("You are rebooting the system. Are you sure you wish to continue? [Y/n]: ")
            if not(prompt.lower() == "y" or prompt.lower == "yes"):
                exit(0)
            request = requests.post(destination+"/api/system/commands/core/reboot", headers=header)
            if request.status_code != 204:
                print(colored("Reboot Failed", 'red', attrs=['bold']))
            else:
                print("Reboot Initialized")
        elif args[2].lower() == "restart": #system restart
            prompt = input("You are restarting the server. Are you sure you wish to continue? [Y/n]: ")
            if not(prompt.lower() == "y" or prompt.lower == "yes"):
                exit(0)
            request = requests.post(destination+"/api/system/commands/core/restart", headers=header)
            if request.status_code != 204:
                print(colored("Restart Failed", 'red', attrs=['bold']))
            else:
                print("Server is restarting")
        elif args[2].lower() == "restart-safe": #system restart-safe
            prompt = input("You are restarting the server into safe mode. Are you sure you wish to continue? [Y/n]: ")
            if not(prompt.lower() == "y" or prompt.lower == "yes"):
                exit(0)
            request = requests.post(destination+"/api/system/commands/core/restart_safe", headers=header)
            if request.status_code != 204:
                print(colored("Restart Failed", 'red', attrs=['bold']))
            else:
                print("Server is restarting into safe mode")

    if args[1].lower() == "files": #file commands
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403: #authentication fail
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()

        if args[2].lower() == "list": #files list
            container = 'files'
            try: #if folder parameter given
                if args[3].startswith("/"): #remove leading slash
                     args[3] = args[3][1:]
                request = requests.get(destination+"/api/files/local/"+args[3], headers=header) #make request
                if request.status_code == 404: #folder not found error
                    print(colored("Folder does not exist", 'red', attrs=['bold']))
                    exit(1)
                print("Listing files in " + args[3])
                container = 'children'
            except IndexError: #if folder parameter not given
                request = requests.get(destination+"/api/files", headers=header)
            data = request.json() #convert to dictionary
            
            longestName=0 # locate longest names to calculate spacing
            longestType=0
            for i in data[container]:
                if len(i['name']) > longestName: longestName = len(i['name'])
                if len(i['type']) > longestType: longestType = len(i['type'])
            
            print(colored("NAME", attrs=['bold']) + (" "*longestName) + colored("TYPE", attrs=['bold']) + (" "*longestType) + colored("SIZE", attrs=['bold'])) #table headings
            longestName+=4
            longestType+=4
            for i in data[container]: #loop through all files and display information
                print(i['name'] + ((longestName-len(i['name']))*" ") + i['type'] + ((longestType-len(i['type']))*" "),end='')
                try: #some files dont have sizes
                    if i['type'] != 'folder': print(str(round(i['size']/1048576.0,2)) + " MB")
                    else: print() #if folder than leave empty
                except KeyError: print()
            if container=='files': print(colored("\nFree space: ", attrs=['bold'])+str(round(data['free']/1073741824.0,3))+" GB") #disk space
            exit(0)
        
        if args[2].lower() == "info":
            try: #remove leading slash
                if args[3].startswith("/"):
                    args[3] = args[3][1:]
            except IndexError:
                print(colored("Not enough arguments given", 'red', attrs=['bold']))
                exit(1)
            request = requests.get(destination+"/api/files/local/"+args[3], headers=header) #make request

            if request.status_code == 404 or request.status_code == 500: #file dont exist
                print(colored("File does not exist", 'red', attrs=['bold']))
                print("Try checking your spelling or including the full path")
                exit(1)
            data = request.json()
            print(colored("Name: ", attrs=['bold'])+data['name'])
            print(colored("Path: ", attrs=['bold'])+data['refs']['resource'].replace(destination+'/api/files/local/',''))
            print(colored("Type: ", attrs=['bold'])+data['type'])
            try:
                print(colored("Size: ", attrs=['bold'])+str(round(data['size']/1048576.0,2))+" MB")
            except KeyError:
                pass
            if data['type'] == 'machinecode':
                try:
                    print(colored("Estimated Print Time: ", attrs=['bold'])+str(datetime.timedelta(seconds=data['gcodeAnalysis']['estimatedPrintTime'])).split(".")[0])
                except KeyError:
                    pass
                try:
                    print(colored("Successful Prints: ", attrs=['bold'])+str(data['prints']['success']))
                except KeyError:
                    pass
                try:
                    print(colored("Failed Prints: ", attrs=['bold'])+str(data['prints']['failure']))
                except KeyError:
                    pass
            exit(0)
            
    if args[1].lower() == "temp": #temp commands
        request = requests.get(destination+"/api/job", headers=header)
        if request.status_code == 403: #authentication fail
            print(colored("403: Authentication failed, is your API key correct?", 'red', attrs=['bold']))
            exit(1)
        data = request.json()

        if args[2].lower() == "status": #temp status
            request = requests.get(destination+"/api/printer/tool", headers=header)
            if request.status_code == 409:
                print(colored("Printer is not connected", 'red', attrs=['bold']))
                exit(1)
            data = request.json()
            print(colored("Extruder Temp: ", attrs=['bold'])+str(data['tool0']['actual'])+"°C")
            print(colored("Extruder Target Temp: ", attrs=['bold'])+str(data['tool0']['target'])+"°C")
            request = requests.get(destination+"/api/printer/bed", headers=header)
            if request.status_code == 409:
                print(colored("Printer is not connected", 'red', attrs=['bold']))
                exit(1)
            data = request.json()
            print(colored("Bed Temp: ", attrs=['bold'])+str(data['bed']['actual'])+"°C")
            print(colored("Bed Temp: ", attrs=['bold'])+str(data['bed']['target'])+"°C")

        elif args[2].lower() == "extruder": #temp extruder
            try:
                if args[3] == "off":
                    args[3] = "0"
                if not args[3].isdigit():
                    print(colored("Invalid argument", "red", attrs=['bold']))
                    exit(1)
                try:
                    if int(args[3]) > int(config['printer']['MaxExtruderTemp']):
                        print(colored("Target is higher than temperature given in config file", "red", attrs=['bold']))
                        exit(1)
                except KeyError:
                    pass
            except IndexError:
                print(colored("Missing argument, please add a temperature", "red", attrs=['bold']))
            request = requests.post(destination+"/api/printer/tool", headers=header, data=json.dumps({"command":"target","targets":{"tool0":int(args[3])}}))
            if request.status_code == 409:
                print(colored("Printer cannot be reached", 'red', attrs=['bold']))
                exit(1)
            elif request.status_code == 204:
                print("Extruder temp has been set to " + args[3] + "°C")
                exit(0)
            else:
                print(colored("Unable to change extruder temp", 'red', attrs=['bold']))
                exit(1)
            
        elif args[2].lower() == "bed": #temp bed
            try:
                if args[3] == "off":
                    args[3] = "0"
                if not args[3].isdigit():
                    print(colored("Invalid argument", "red", attrs=['bold']))
                try:
                    if int(args[3]) > int(config['printer']['MaxBedTemp']):
                        print(colored("Target is higher than temperature given in config file", "red", attrs=['bold']))
                        exit(1)
                except KeyError:
                    pass
            except IndexError:
                print(colored("Missing argument, please add a temperature", "red", attrs=['bold']))
            request = requests.post(destination+"/api/printer/bed", headers=header, data=json.dumps({"command":"target","target":int(args[3])}))
            if request.status_code == 409:
                print(colored("Printer cannot be reached", 'red', attrs=['bold']))
                exit(1)
            elif request.status_code == 204:
                print("Bed temp has been set to " + args[3] + "°C")
                exit(0)
            else:
                print(colored("Unable to change bed temp", 'red', attrs=['bold']))
                exit(1)


except IndexError: #not enough arguments
    print(colored("Not enough arguments provided", 'red', attrs=['bold']))
    exit(1)

#TODO Limit temperature in config file
#TODO Connect to printer
#TODO Upload files