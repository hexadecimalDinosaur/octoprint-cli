#!/usr/bin/python3
import argparse
import configparser
from os.path import expanduser
import os
from api import api
import sys
import datetime
import time
import math

config = configparser.ConfigParser()
parser = argparse.ArgumentParser(prog="octoprint-cli", description="Command line tool for controlling OctoPrint 3D printer servers", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
optionals = parser.add_argument_group()
subparsers = parser.add_subparsers()

def loadConfig(path):
    configComplete = True
    configExists = False
    try:
        open(os.path.join(path))
        config.read(os.path.join(path))
        config['server']['ServerAddress']
        config['server']['ApiKey']
        return True
    except KeyError:
        return False
    except FileNotFoundError:
        return False

if loadConfig(os.path.join(sys.path[0],'config.ini')):
    pass
elif loadConfig(os.path.expanduser('~/.config/octoprint-cli.ini')):
    pass
else:
    print("Configuration file is not complete or does not exist")
    sys.exit(1)

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

destination = config['server']['ServerAddress']
key = config['server']['ApiKey']

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

def version(args):
    data=caller.getVersionInfo()
    print("OctoPrint v" + data['server'] + " - API v" + data['api'])
    sys.exit(0)

com_version = subparsers.add_parser('version', description='get OctoPrint version')
com_version.set_defaults(func=version)

def continuous(args):
    try:
        while True: 
            lines = 0
            if not(caller.getState() in ('Operational', 'Printing', 'Paused', 'Pausing', 'Cancelling')):
                print(colored(caller.getState(),'red',attrs=['bold']))
                data = caller.get('/api/connection')
                print(colored("Printer Profile: ", attrs=['bold']) + data['options']['printerProfiles'][0]['name'])
                print(colored("Port: ", attrs=['bold']) + str(data['current']['port']))
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
                print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Print Time Left: ", attrs=['bold'])+str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
                print()
                print(colored("Temperature Status", attrs=['bold','underline']))
                data2 = caller.get('/api/printer')
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
                print()
                print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                lines+=13
            if caller.getState() == 'Paused':
                data = caller.get('/api/job')
                print(colored('Paused', 'yellow', attrs=['bold']))
                print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Progress: ", attrs=['bold'])+str(round(data['progress']['completion'],2))+"%")
                print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Print Time Left: ", attrs=['bold'])+str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
                print()
                print(colored("Temperature Status", attrs=['bold','underline']))
                data2 = caller.get('/api/printer')
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
                print()
                print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                lines+=13
            if caller.getState() == 'Pausing':
                data = caller.get('/api/job')
                print(colored('Pausing', 'yellow', attrs=['bold']))
                print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Progress: ", attrs=['bold'])+str(round(data['progress']['completion'],2))+"%")
                print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print(colored("Print Time Left: ", attrs=['bold'])+str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
                print()
                print(colored("Temperature Status", attrs=['bold','underline']))
                data2 = caller.get('/api/printer')
                print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
                print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
                print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
                print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
                print()
                print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                lines+=13
            if caller.getState() == 'Cancelling':
                data = caller.get('/api/job')
                print(colored('Cancelling', 'red', attrs=['bold']))
                print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
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
                sys.stdout.write("\033[F\033[K")
    except KeyboardInterrupt:
        print(colored("Continuous output terminated", attrs=['bold']))
        sys.exit(0)

com_continuous = subparsers.add_parser('continuous', description='get continuous refreshing status with temperature information and progress information')
com_continuous.set_defaults(func=continuous)

def layers(args):
    data=caller.get("/plugin/DisplayLayerProgress/values")
    if data==404:
        print(colored("The DisplayLayerProgress is not installed or enabled on the OctoPrint server", 'red', attrs=['bold']))
        sys.exit(1)
    elif type(data) == dict and caller.getState() in ('Printing', 'Paused', 'Pausing', 'Finishing'):
        print(colored("Current Layer: ", 'white', attrs=['bold'])+data['layer']['current']+"/"+data['layer']['total'])
        print(colored("Current Height: ", 'white', attrs=['bold'])+data['height']['current']+'/'+data['height']['totalFormatted']+'mm')
        print(colored("Average Layer Duration: ", 'white', attrs=['bold'])+data['layer']['averageLayerDuration'].replace('h','').replace('s','').replace('m',''))
        print(colored("Last Layer Duration: ", 'white', attrs=['bold'])+data['layer']['lastLayerDuration'].replace('h','').replace('s','').replace('m',''))
        sys.exit(0)
    else:
        print(colored('Unable to retreive layer information', 'red', attrs=['bold']))
        sys.exit(1)

com_layers = subparsers.add_parser('layers', description='get layer information from the DisplayLayerProgress plugin')
com_layers.set_defaults(func=layers)

def gcode(args):
    command = args.command
    request = caller.post('/api/printer/command', {'command':command})
    if request != 204:
        print(colored('G-code execution failed', 'red', attrs=['bold']))
        sys.exit(1)
    sys.exit(0)

com_gcode = subparsers.add_parser('gcode', description='run gcode on printer')
com_gcode.add_argument('command')
com_gcode.set_defaults(func=gcode)

com_print = subparsers.add_parser('print', description='print job commands')
coms_print = com_print.add_subparsers()

def print_status(args):
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

com_print_status = coms_print.add_parser('status', description='view print job status')
com_print_status.set_defaults(func=print_status)

def print_select(args):
    path = args.path
    if path.startswith('/'):
        path = path[1:]
    code = caller.selectFile(path)
    if code == 404:
        print(colored('File does not exist', 'red', attrs=['bold']))
        sys.exit(1)
    if code == 204:
        print(path+" has been loaded")
        sys.exit(0)
    elif code != 204:
        print(colored('Unable to select file'))
        sys.exit(1)

com_print_select = coms_print.add_parser('select', description='select file on server to load')
com_print_select.set_defaults(func=print_select)
com_print_select.add_argument('path')

def print_start(args):
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

com_print_start = coms_print.add_parser('start', description='start print job on selected file')
com_print_start.set_defaults(func=print_start)

def print_cancel(args):
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

com_print_cancel = coms_print.add_parser('cancel', description='cancel current print job')
com_print_cancel.set_defaults(func=print_cancel)

def print_pause(args):
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

com_print_pause = coms_print.add_parser('pause', description='pause current print job')
com_print_pause.set_defaults(func=print_pause)

def print_resume(args):
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

com_print_resume = coms_print.add_parser('resume', description='resume current print job')
com_print_resume.set_defaults(func=print_resume)

com_connection = subparsers.add_parser('connection', description='printer connection commands')
coms_connections = com_connection.add_subparsers()

def connection_status(args):
    data = caller.get('/api/connection')
    if data['current']['state'] in ('Printing', 'Operational'):
        print(colored(data['current']['state'], 'green', attrs=['bold']))
        print(colored("Printer Profile: ", attrs=['bold']) + data['options']['printerProfiles'][0]['name'])
        print(colored("Port: ", attrs=['bold']) + data['current']['port'])
        print(colored("Baudrate: ", attrs=['bold']) + str(data['current']['baudrate']))
    elif data['current']['state'] == 'Closed': #disconnected
        print(colored("Printer Disconnected", 'red', attrs=['bold']))
        print(colored("Ports: ", attrs=['bold'])+",".join(data['options']['ports']))
        print(colored("Baudrates: ", attrs=['bold'])+", ".join(list(map(str,data['options']['baudrates']))))
    elif data['current']['state'].startswith("Error"): #connection error
        print(colored("Error", 'red', attrs=['bold']))
        print(colored("Error: ", attrs=['bold'])+data['current']['state'][7:])
        print(colored("Ports: ", attrs=['bold'])+",".join(data['options']['ports']))
        print(colored("Baudrates: ", attrs=['bold'])+", ".join(list(map(str,data['options']['baudrates']))))

com_connection_status = coms_connections.add_parser('status', description='get printer connection status')
com_connection_status.set_defaults(func=connection_status)

def connection_connect(args):
    data = {'command':'connect', 'Content-Type':'application/json'}
    if args.port:
        data['port'] = args.port
    if args.baudrate:
        data['baudrate'] = args.baudrate
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

com_connection_connect = coms_connections.add_parser('connect', description='connect to printer')
com_connection_connect.set_defaults(func=connection_connect)
com_connection_connect.add_argument('-p', '--port', type=str, dest='port', action='store', help='serial port')
com_connection_connect.add_argument('-b', '--baudrate', type=int, dest='baudrate', action='store', help='connection baudrate')

def connection_disconnect(args):
    code = caller.post("/api/connection", {"command":"disconnect"})
    if code == 204:
        print("Printer disconnected")
        sys.exit(0)
    else:
        print(colored("Unable to disconnect from printer", 'red', attrs=['bold']))
        sys.exit(1)

com_connection_disconnect = coms_connections.add_parser('disconnect', description='disconnect from printer')
com_connection_disconnect.set_defaults(func=connection_disconnect)

def help(args):
    print(parser.format_help())
    sys.exit(0)

com_help = subparsers.add_parser('help')
com_help.set_defaults(func=help) #TODO individual subcommand help pages

options = parser.parse_args()
try:
    options.func(options)
except AttributeError as e:
    print(colored("Invalid or Missing Arguments", 'red', attrs=['bold']))
    print(parser.format_help())
    sys.exit(2)