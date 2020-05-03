#!/usr/bin/python3
import configparser
from os.path import expanduser
import os
from api import api
import sys
import datetime

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
octoprint-cli temp bed [target]         set bed target temperature"""

try:
    if args[1] == 'help':
        print(helpMsg)
        sys.exit(0)

    if args[1] == 'version':
        data=caller.getVersionInfo()
        print("OctoPrint v" + data['server'] + " - API v" + data['api'])
        sys.exit(0)

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
                print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
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
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
            elif state == 'Paused':
                print(colored("Paused", 'yellow', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
                print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
            elif state == 'Pausing':
                print(colored("Pausing", 'yellow', attrs=['bold']))
                print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Total Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Estimated Print Time Left: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
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


    else:
        print(colored("Invalid arguments", 'red', attrs=['bold']))
        sys.exit(1)

except IndexError:
    print(colored("Not enough arguments specified", 'red', attrs=['bold']))
    sys.exit(1)