#!/usr/bin/python3
import configparser
from os.path import expanduser
import os
from api import api
import sys
import datetime
import time
import math

config = configparser.ConfigParser()
configComplete = True
configExists = False
if os.path.exists(f"{os.path.dirname(__file__)}{os.sep}config.ini"):
    config.read(os.path.join(sys.path[0],'config.ini'))
    configExists = True
else:
    if os.path.exists(expanduser('~/.config/octoprint-cli.ini')):
        config.read(expanduser('~/.config/octoprint-cli.ini'))
        configExists = True

try:
    key = config['server']['ApiKey']
    destination = config['server']['ServerAddress']
except KeyError:
    configComplete = False

color = True #termcolor configuration
if os.name=='nt':
    def colored(*args, attrs=None):
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

helpMsg = """octoprint-cli
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
octoprint-cli files upload [file]       upload file to OctoPrint server storage
octoprint-cli system restart            restart OctoPrint server
octoprint-cli system restart-safe       restart OctoPrint server to safe mode
octoprint-cli system reboot             reboot server
octoprint-cli system shutdown           shutdown server
octoprint-cli continuous                get refreshing continuous status
octoprint-cli layers                    view DisplayLayerProgress information"""

try:
    if args[1] == 'help':
        print(helpMsg)
        sys.exit(0)

    elif args[1] == 'version':
        data=caller.getVersionInfo()
        print("OctoPrint v" + data['server'] + " - API v" + data['api'])
        sys.exit(0)

    elif args[1] == 'continuous':
        try:
            while True: 
                lines = 0
                if not(caller.getState() in ('Operational', 'Printing', 'Paused', 'Pausing', 'Cancelling')):
                    print(colored(caller.getState(),'red',attrs=['bold']))
                    data = caller.get('/api/connection')
                    print(colored("Printer Profile: ", attrs=['bold']) + data['options']['printerProfiles'][0]['name'])
                    if data['current']['port'] != None:
                        print(colored("Ports: ", attrs=['bold']) + data['current']['port'])
                    else:
                        print(colored("Ports: ", attrs=['bold'])+"None")
                    print(colored("Baudrate: ", attrs=['bold']) + str(data['current']['baudrate']))
                    lines = 4
                if caller.getState() == 'Operational':
                    data = caller.get('/api/job')
                    print(colored('Printer Operational', 'green', attrs=['bold']))
                    if data['job']['file']['name']:
                        print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                        print(colored("Estimated Print Time: ", attrs=['bold']) + caller.getTotalTime())
                        print()
                        lines+=3
                    print(colored("Temperature Status", attrs=['bold','underline']))
                    data2 = caller.get('/api/printer')
                    print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                    print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                    print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                    print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
                    lines+=6
                if caller.getState() == 'Printing':
                    data = caller.get('/api/job')
                    print(colored('Printing', 'green', attrs=['bold']))
                    print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                    print(colored("Progress: ", attrs=['bold'])+str(round(data['progress']['completion'],2))+"%")
                    print(colored("Estimated Print Time: ", attrs=['bold']) + caller.getTotalTime())
                    print(colored("Print Time Left: ", attrs=['bold'])+caller.getTimeLeft())
                    print()
                    print(colored("Temperature Status", attrs=['bold','underline']))
                    data2 = caller.get('/api/printer')
                    print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                    print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                    print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                    print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
                    print()
                    data=caller.get("/plugin/DisplayLayerProgress/values")
                    if type(data) is dict:
                        print(colored("Layer Information", 'white', attrs=['bold']))
                        print(colored("Current Layer: ", 'white', attrs=['bold'])+data['layer']['current']+"/"+data['layer']['total'])
                        print(colored("Current Height: ", 'white', attrs=['bold'])+data['height']['current']+'/'+data['height']['totalFormatted']+'mm')
                        print()
                        lines+=4
                    data = caller.get('/api/job')
                    print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                    lines+=13
                if caller.getState() == 'Paused':
                    data = caller.get('/api/job')
                    print(colored('Paused', 'yellow', attrs=['bold']))
                    print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                    print(colored("Progress: ", attrs=['bold'])+str(round(data['progress']['completion'],2))+"%")
                    print(colored("Estimated Print Time: ", attrs=['bold']) + caller.getTotalTime())
                    print(colored("Print Time Left: ", attrs=['bold'])+caller.getTimeLeft())
                    print()
                    print(colored("Temperature Status", attrs=['bold','underline']))
                    data2 = caller.get('/api/printer')
                    print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                    print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                    print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                    print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
                    print()
                    data=caller.get("/plugin/DisplayLayerProgress/values")
                    if type(data) is dict:
                        print(colored("Layer Information", 'white', attrs=['bold']))
                        print(colored("Current Layer: ", 'white', attrs=['bold'])+data['layer']['current']+"/"+data['layer']['total'])
                        print(colored("Current Height: ", 'white', attrs=['bold'])+data['height']['current']+'/'+data['height']['totalFormatted']+'mm')
                        print()
                        lines+=4
                    data = caller.get('/api/job')
                    print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                    lines+=13
                if caller.getState() == 'Pausing':
                    data = caller.get('/api/job')
                    print(colored('Pausing', 'yellow', attrs=['bold']))
                    print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                    print(colored("Progress: ", attrs=['bold'])+str(round(data['progress']['completion'],2))+"%")
                    print(colored("Estimated Print Time: ", attrs=['bold']) + caller.getTotalTime())
                    print(colored("Print Time Left: ", attrs=['bold'])+caller.getTimeLeft())
                    print()
                    print(colored("Temperature Status", attrs=['bold','underline']))
                    data2 = caller.get('/api/printer')
                    print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                    print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                    print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                    print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
                    print()
                    data=caller.get("/plugin/DisplayLayerProgress/values")
                    if type(data) is dict:
                        print(colored("Layer Information", 'white', attrs=['bold']))
                        print(colored("Current Layer: ", 'white', attrs=['bold'])+data['layer']['current']+"/"+data['layer']['total'])
                        print(colored("Current Height: ", 'white', attrs=['bold'])+data['height']['current']+'/'+data['height']['totalFormatted']+'mm')
                        print()
                        lines+=4
                    data = caller.get('/api/job')
                    print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                    lines+=13
                if caller.getState() == 'Cancelling':
                    data = caller.get('/api/job')
                    print(colored('Cancelling', 'red', attrs=['bold']))
                    print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                    print(colored("Estimated Print Time: ", attrs=['bold']) + caller.getTotalTime())
                    print()
                    print(colored("Temperature Status", attrs=['bold','underline']))
                    data2 = caller.get('/api/printer')
                    print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                    print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                    print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                    print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
                    lines+=9

                time.sleep(3)
                for i in range(lines):
                    sys.stdout.write("\033[K\033[F\033[K")
        except KeyboardInterrupt:
            print(colored("Continuous output terminated", attrs=['bold']))
            sys.exit(0)

    elif args[1] == 'layers':
        data=caller.get("/plugin/DisplayLayerProgress/values")
        if data==404:
            print(colored("The DisplayLayerProgress is not installed or enabled on the OctoPrint server", 'red', attrs=['bold']))
            sys.exit(1)
        elif type(data) is dict and caller.getState() in ('Printing', 'Paused', 'Pausing', 'Finishing'):
            print(colored("Current Layer: ", 'white', attrs=['bold'])+data['layer']['current']+"/"+data['layer']['total'])
            print(colored("Current Height: ", 'white', attrs=['bold'])+data['height']['current']+'/'+data['height']['totalFormatted']+'mm')
            print(colored("Average Layer Duration: ", 'white', attrs=['bold'])+data['layer']['averageLayerDuration'].replace('h','').replace('s','').replace('m',''))
            print(colored("Last Layer Duration: ", 'white', attrs=['bold'])+data['layer']['lastLayerDuration'].replace('h','').replace('s','').replace('m',''))
            sys.exit(0)
        else:
            print(colored('Unable to retreive layer information', 'red', attrs=['bold']))
            sys.exit(1)

    elif args[1:3] == ['print', 'status']:
        state = caller.getState()
        
        if state == 'Offline': #printer disconnected
            print(colored("Printer Disconnected", 'red', attrs=['bold']))
        elif state.startswith('Offline'): #Offline status with error message following
            print(colored("Printer Disconnected", 'red', attrs=['bold']))
            print(state)
        elif state.startswith('Error'): #Error status
            print(colored("❌ Error", 'red', attrs=['bold']))
            print(colored("Error: ", attrs=['bold'])+state[7:])
        else:
            selectedFile = caller.getFile()
            data = caller.get("/api/job")
            data2 = caller.get("/api/printer")
            
            if state == 'Operational' and selectedFile:
                print(colored("Printer Operational", 'green', attrs=['bold']))
                print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Print Time: ", attrs=['bold']) + caller.getTotalTime())
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
            elif state == 'Operational':
                print(colored("Printer Operational", 'green', attrs=['bold']))
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
            elif state == 'Printing':
                print(colored("Printing", 'green', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + caller.getTotalTime())
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + caller.getTimeLeft())
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
            elif state == 'Paused':
                print(colored("Paused", 'yellow', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + caller.getTotalTime())
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + caller.getTimeLeft())
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
            elif state == 'Pausing':
                print(colored("Pausing", 'yellow', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + caller.getTotalTime())
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + caller.getTimeLeft())
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
            elif state == 'Cancelling':
                print(colored("Cancelling", 'red', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
            elif state == 'Finishing':
                print(colored("Finishing", 'green', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + caller.getTotalTime())
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + caller.getTimeLeft())
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
        sys.exit(0)

    elif args[1:3] == ['print', 'select']:
        try:
            if args[3].startswith('/'):
                args[3] = args[3][1:]
        except IndexError:
            print(colored("Not enough arguments specified", 'red', attrs=['bold']))
            sys.exit(1)
        code = caller.selectFile(args[3])
        if code == 404:
            print(colored('File does not exist', 'red', attrs=['bold']))
            sys.exit(1)
        if code == 204:
            print(args[3]+" has been loaded")
        elif code != 204:
            print(colored('Unable to select file'))
            sys.exit(1)

    elif args[1:3] == ['print', 'start']:
        if caller.getFile() == None:
            print(colored("No file has been loaded", 'red', attrs=['bold']))
            sys.exit(1)
        code = caller.printRequests('start')
        if code == 409 and caller.getState() in ('Printing', 'Paused', 'Pausing', 'Cancelling'):
            print(colored("Printer is already printing", 'red', attrs=['bold']))
            sys.exit(1)
        elif code == 409:
            print(colored("Unable to print", 'red', attrs=['bold']))
            sys.exit(1)
        elif code == 204:
            print(colored("Starting print",'green',attrs=['bold']))
            sys.exit(0)

    elif args[1:3] == ['print', 'cancel']:
        code = caller.printRequests('cancel')
        if code == 409:
            print(colored('No print job is running', 'red', attrs=['bold']))
            sys.exit(1)
        elif code == 204:
            print('Print job cancelling')
            sys.exit(0)
        else:
            print(colored('Unable to cancel', 'red', attrs=['bold']))
            sys.exit(1)
    
    elif args[1:3] == ['print', 'pause']:
        code = caller.pauseRequests('pause')
        if code == 409:
            print(colored('No print job is running', 'red', attrs=['bold']))
            sys.exit(1)
        elif code == 204:
            print('Print job pausing')
            sys.exit(0)
        else:
            print(colored('Unable to pause', 'red', attrs=['bold']))
            sys.exit(1)
    
    elif args[1:3] == ['print', 'resume']:
        code = caller.pauseRequests('resume')
        if code == 409:
            print(colored('No print job is running', 'red', attrs=['bold']))
            sys.exit(1)
        elif code == 204:
            print('Print job resuming')
            sys.exit(0)
        else:
            print(colored('Unable to resume', 'red', attrs=['bold']))
            sys.exit(1)

    elif args[1:3] == ['connection', 'status']:
        data = caller.get('/api/connection')

        if data['current']['state'] in ('Printing', 'Operational'):
            print(colored("✅"+data['current']['state'], 'green', attrs=['bold']))
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

    elif args[1:3] == ['connection', 'connect']:
        data = {'command':'connect'}
        port = ''
        baudrate = 0
        try:
            if args[3] == 'port':
                port = args[4]
            if args[3] == 'baudrate':
                baudrate = int(args[4])
        except IndexError:
            pass
        except ValueError:
            print(colored("Baudrate needs to be an integer", 'red', attrs=['bold']))
        try:
            if args[5] == 'port':
                port = args[6]
            if args[5] == 'baudrate':
                baudrate = int(args[6])
        except IndexError:
            pass
        except ValueError:
            print(colored("Baudrate needs to be an integer", 'red', attrs=['bold']))
        if port != '':
            data['port'] = port
        if baudrate != 0:
            data['baudrate'] = baudrate
        code = caller.post("/api/connection", data)
        if code == 400:
            print(colored("Port or baudrate is incorrect", 'red', attrs=['bold']))
            sys.exit(1)
        elif code == 204 and caller.getState().startswith("Error"):
            print(colored("Unable to connect to printer", 'red', attrs=['bold']))
            print(caller.getState())
            sys.exit(1)
        elif code == 204:
            print(colored("Printer connected", 'green', attrs=['bold']))
            sys.exit(0)
        else:
            print(colored("Unable to connect to printer", 'red', attrs=['bold']))
            sys.exit(1)

    elif args[1:3] == ['connection', 'disconnect']:
        code = caller.post("/api/connection", {"command":"disconnect"})
        if code == 204:
            print("Printer disconnected")
            sys.exit(0)
        else:
            print(colored("Unable to disconnect from printer", 'red', attrs=['bold']))
            sys.exit(1)

    elif args[1:3] == ['temp', 'status']:
        data = caller.get("/api/printer")
        if data == 409:
            print(colored("Printer is not operational", 'red', attrs=['bold']))
            sys.exit(1)
        if type(data) is dict:
            print(colored("Extruder Temp: ", attrs=['bold'])+str(data['temperature']['tool0']['actual'])+"°C")
            print(colored("Extruder Target: ", attrs=['bold'])+str(data['temperature']['tool0']['target'])+"°C")
            print(colored("Bed Temp: ", attrs=['bold'])+str(data['temperature']['bed']['actual'])+"°C")
            print(colored("Bed Target: ", attrs=['bold'])+str(data['temperature']['bed']['target'])+"°C")
        
    elif args[1:3] == ['temp', 'extruder']:
        if args[3] == 'off':
            args[3] = '0'
        if not(args[3].isdigit()):
            print(colored("Invalid arguments", 'red', attrs=['bold']))
            sys.exit(1)
        try:
            if int(args[3]) > int(config['print']['MaxExtruderTemp']):
                print(colored("Target temp is higher than the limit set in the configuration file", 'red', attrs=['bold']))
                sys.exit(1)
        except KeyError:
            pass
        code = caller.post("/api/printer/tool", {'command':'target','targets':{'tool0':int(args[3])}})
        if code == 204:
            print(colored("Extruder temp set to " + args[3]+"°C", 'green', attrs=['bold']))
            sys.exit(0)
        elif code == 409:
            print(colored("Printer is not operational", 'red', attrs=['bold']))
            sys.exit(1)
        else:
            print(colored("Unable to change temperature", 'red', attrs=['bold']))
            sys.exit(1)

    elif args[1:3] == ['temp', 'bed']:
        if args[3] == 'off':
            args[3] = '0'
        if not(args[3].isdigit()):
            print(colored("Invalid arguments", 'red', attrs=['bold']))
            sys.exit(1)
        try:
            if int(args[3]) > int(config['print']['MaxBedTemp']):
                print(colored("Target temp is higher than the limit set in the configuration file", 'red', attrs=['bold']))
                sys.exit(1)
        except KeyError:
            pass
        code = caller.post("/api/printer/bed", {'command':'target','target':int(args[3])})
        if code == 204:
            print(colored("Bed temp set to " + args[3]+"°C", 'green', attrs=['bold']))
            sys.exit(0)
        elif code == 409:
            print(colored("Printer is not operational", 'red', attrs=['bold']))
            sys.exit(1)
        else:
            print(colored("Unable to change temperature", 'red', attrs=['bold']))
            sys.exit(1)

    elif args[1:3] == ['system', 'restart']:
        prompt = input(colored("You are restarting the server. Are you sure you wish to continue?",attrs=['bold'])+" [Y/n]: ")
        if not(prompt.lower() == "y" or prompt.lower == "yes"):
            sys.exit(0)
        code = caller.post("/api/system/commands/core/restart",{})
        if code != 204:
            print(colored("Unable to restart",'red',attrs=['bold']))
            sys.exit(1)
        else:
            print("OctoPrint is restarting")

    elif args[1:3] == ['system', 'restart-safe']:
        prompt = input(colored("You are restarting the server to safe mode. Are you sure you wish to continue?",attrs=['bold'])+" [Y/n]: ")
        if not(prompt.lower() == "y" or prompt.lower == "yes"):
            sys.exit(0)
        code = caller.post("/api/system/commands/core/restart_safe",{})
        if code != 204:
            print(colored("Unable to restart",'red',attrs=['bold']))
            sys.exit(1)
        else:
            print("OctoPrint is restarting to safe mode")

    elif args[1:3] == ['system', 'reboot']:
        prompt = input(colored("You are rebooting the server. Are you sure you wish to continue?",attrs=['bold'])+" [Y/n]: ")
        if not(prompt.lower() == "y" or prompt.lower == "yes"):
            sys.exit(0)
        code = caller.post("/api/system/commands/core/reboot",{})
        if code != 204:
            print(colored("Unable to reboot",'red',attrs=['bold']))
            sys.exit(1)
        else:
            print("Server is rebooting")

    elif args[1:3] == ['system', 'shutdown']:
        prompt = input(colored("You are shutting down the server. Are you sure you wish to continue?",attrs=['bold'])+" [Y/n]: ")
        if not(prompt.lower() == "y" or prompt.lower == "yes"):
            sys.exit(0)
        code = caller.post("/api/system/commands/core/shutdown",{})
        if code != 204:
            print(colored("Unable to shutdown",'red',attrs=['bold']))
            sys.exit(1)
        else:
            print("Server is shutting down")

    elif args[1:3] == ['files', 'list']:
        container = 'files'
        try:
            if args[3].startswith("/"):
                    args[3] = args[3][1:]
            if args[3].endswith("/"):
                    args[3] = args[3][:-1]

            data = caller.get("/api/files/local/"+args[3])
            if data == 404:
                print(colored("Folder does not exist", 'red', attrs=['bold']))
                sys.exit(1)
            print("Listing files in " + args[3])
            container = 'children'
        except IndexError:
            data = caller.get("/api/files")
        
        longestName=0
        longestType=0
        for i in data[container]:
            if len(i['name']) > longestName: longestName = len(i['name'])
            if len(i['type']) > longestType: longestType = len(i['type'])
        
        print(colored("NAME", attrs=['bold']) + (" "*longestName) + colored("TYPE", attrs=['bold']) + (" "*longestType) + colored("SIZE", attrs=['bold'])) #table headings
        longestName+=4
        longestType+=4
        for i in data[container]:
            print(i['name'] + ((longestName-len(i['name']))*" ") + i['type'] + ((longestType-len(i['type']))*" "),end='')
            try:
                if i['type'] != 'folder': print(str(round(i['size']/1048576.0,2)) + " MB")
                else: print()
            except KeyError: print()
        if container=='files': print(colored("\nFree space: ", attrs=['bold'])+str(round(data['free']/1073741824.0,3))+" GB") #disk space
        sys.exit(0)

    elif args[1:3] == ['files', 'info']:
        if args[3].startswith("/"):
            args[3] = args[3][1:]
        data = caller.get("/api/files/local/"+args[3])
        if data == 404 or data == 500:
            print(colored("File or folder not found", 'red', attrs=['bold']))
            sys.exit(1)
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
        sys.exit(0)

    elif args[1:3] == ['files', 'upload']:
        if not os.path.exists(args[3]):
            print(colored("File not found", 'red', attrs=['bold']))
            sys.exit(1)
        path=""
        data = caller.fileUpload(args[3])
        
        if data==415:
            print(colored("Invalid file type", 'red', attrs=['bold']))
            sys.exit(1)
        if data==409:
            print(colored("File upload is in conflict with server state", 'red', attrs=['bold']))
            sys.exit(1)
        if type(data) is dict:
            print(colored("File uploaded to OctoPrint", 'green', attrs=['bold']))
            sys.exit(0)
        else:
            print(colored("Unable to upload file", 'red', attrs=['bold']))
            sys.exit(0)

    else:
        print(colored("Invalid arguments", 'red', attrs=['bold']))
        sys.exit(1)

except IndexError:
    print(colored("Not enough arguments specified", 'red', attrs=['bold']))
    sys.exit(1)
