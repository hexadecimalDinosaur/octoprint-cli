#!/usr/bin/python3
import argparse
import configparser
import os
import sys
import datetime
import time
import math
import requests
from termcolor import colored
from __init__ import __version__

config = configparser.ConfigParser()
parser = argparse.ArgumentParser(prog="octoprint-cli", description="Command line tool for controlling OctoPrint 3D printer servers", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
optionals = parser.add_argument_group()
subparsers = parser.add_subparsers()
caller = None
destination = None
key = None

class api:
    address = ""
    XapiKey = ""
    header = {}

    def __init__(self, key, destination):
        """api caller constructor method"""
        self.address = destination
        self.XapiKey = key
        self.header['X-API-Key']=key

    def get(self, target):
        request = requests.get(self.address+target, headers=self.header)
        if request.status_code != 200:
            return request.status_code
        return request.json()

    def post(self, target, data):
        request = requests.post(self.address+target, headers=self.header, json=(data))
        return request.status_code

    def connectionTest(self):
        try:
            if isinstance(self.get("/api/version"),dict):
                return True
            else:
                return False
        except requests.ConnectionError:
            return False

    def authTest(self):
        if isinstance(self.get("/api/job"),dict):
            return True
        else:
            return False

    def getVersionInfo(self):
        return self.get("/api/version")

    def getState(self):
        return self.get("/api/job")['state']

    def getFile(self):
        return self.get("/api/job")['job']['file']['name']

    def getProgress(self):
        return self.get("/api/job")['progress']['completion']

    def getTimeLeft(self):
        time = self.get("/api/job")['progress']['printTimeLeft']
        hours = int(time//3600)
        if len(str(hours))==1:
            hours = "0"+str(hours)
        time = time%3600
        minutes = int(time//60)
        time = int(time%60)
        if len(str(minutes))==1:
            minutes = "0"+str(minutes)
        time = int(time%60)
        if len(str(time))==1:
            time = "0"+str(time)
        return str(hours)+":"+str(minutes)+":"+str(time)

    def getTotalTime(self):
        time = self.get("/api/job")['job']['estimatedPrintTime']
        hours = int(time//3600)
        if len(str(hours))==1:
            hours = "0"+str(hours)
        time = time%3600
        minutes = int(time//60)
        time = int(time%60)
        if len(str(minutes))==1:
            minutes = "0"+str(minutes)
        return str(hours)+":"+str(minutes)

    def selectFile(self, fileName):
        return self.post("/api/files/local/"+fileName, {'command':'select'})

    def printRequests(self, command):
        return self.post("/api/job", {'command':command})

    def pauseRequests(self, action):
        return self.post("/api/job", {'command':'pause', 'action':action})

    def fileUpload(self, file):
        fle = {'file':open(file,'rb'), 'filename':file}
        request = requests.post(self.address+"/api/files/local", headers=self.header, files=fle)
        if request.status_code == 201:
            return request.json()
        return request.status_code


def loadConfig(path):
    try:
        open(os.path.join(path))
        config.read(os.path.join(path))
        if config['server']['ServerAddress']:
            pass
        if config['server']['ApiKey']:
            pass
        return True
    except KeyError:
        return False
    except FileNotFoundError:
        return False

def init_config():
    global destination
    global key
    destination = config['server']['ServerAddress']
    key = config['server']['ApiKey']

    if not(destination.startswith('http://') or destination.startswith('https://')): #add http if missing
        destination = "http://" + destination
    if destination.endswith('/'): #remove trailing slash
        destination = destination[:-1]
    global caller
    caller = api(key,destination)

def version(args):
    data=caller.getVersionInfo()
    print("OctoPrint v" + data['server'] + " - API v" + data['api'])
    sys.exit(0)

com_version = subparsers.add_parser('version', description='get OctoPrint version', help='get OctoPrint version')
com_version.set_defaults(func=version)

def continuous(args):
    def tempPrint():
        print(colored("Temperature Status", attrs=['bold','underline']))
        data2 = caller.get('/api/printer')
        print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
        print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
        print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
        print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
    def jobPrint():
        data = caller.get('/api/job')
        print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
        print(colored("Progress: ", attrs=['bold'])+str(round(data['progress']['completion'],2))+"%")
        print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
        print(colored("Print Time Left: ", attrs=['bold'])+str(datetime.timedelta(seconds=data['progress']['printTimeLeft'])).split(".")[0])
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
                tempPrint()
                lines+=6
            if caller.getState() == 'Printing':
                data = caller.get('/api/job')
                jobPrint()
                print()
                tempPrint()
                print()
                print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                lines+=13
            if caller.getState() == 'Paused':
                data = caller.get('/api/job')
                print(colored('Paused', 'yellow', attrs=['bold']))
                jobPrint()
                print()
                tempPrint()
                print()
                print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                lines+=13
            if caller.getState() == 'Pausing':
                data = caller.get('/api/job')
                print(colored('Pausing', 'yellow', attrs=['bold']))
                jobPrint()
                print()
                tempPrint()
                print()
                print("Progress: |"+("#"*math.floor(data['progress']['completion']/5))+("—"*math.ceil((100-data['progress']['completion'])/5))+"| "+str(round(data['progress']['completion'],2))+"% Complete")
                lines+=13
            if caller.getState() == 'Cancelling':
                data = caller.get('/api/job')
                print(colored('Cancelling', 'red', attrs=['bold']))
                print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
                print(colored("Estimated Print Time: ", attrs=['bold']) + str(datetime.timedelta(seconds=data['job']['estimatedPrintTime'])).split(".")[0])
                print()
                tempPrint()
                lines+=9

            time.sleep(3)
            sys.stdout.write("\033[F\033[K"*lines)
    except KeyboardInterrupt:
        print(colored("Continuous output terminated", attrs=['bold']))
        sys.exit(0)

com_continuous = subparsers.add_parser('continuous', description='get continuous refreshing status with temperature information and progress information', help='get continuous refreshing status with temperature information and progress information')
com_continuous.set_defaults(func=continuous)

def layers(args):
    data=caller.get("/plugin/DisplayLayerProgress/values")
    if data==404:
        print(colored("The DisplayLayerProgress is not installed or enabled on the OctoPrint server", 'red', attrs=['bold']))
        sys.exit(1)
    elif isinstance(data, dict) and caller.getState() in ('Printing', 'Paused', 'Pausing', 'Finishing'):
        print(colored("Current Layer: ", 'white', attrs=['bold'])+data['layer']['current']+"/"+data['layer']['total'])
        print(colored("Current Height: ", 'white', attrs=['bold'])+data['height']['current']+'/'+data['height']['totalFormatted']+'mm')
        print(colored("Average Layer Duration: ", 'white', attrs=['bold'])+data['layer']['averageLayerDuration'].replace('h','').replace('s','').replace('m',''))
        print(colored("Last Layer Duration: ", 'white', attrs=['bold'])+data['layer']['lastLayerDuration'].replace('h','').replace('s','').replace('m',''))
        sys.exit(0)
    else:
        print(colored('Unable to retreive layer information', 'red', attrs=['bold']))
        sys.exit(1)

com_layers = subparsers.add_parser('layers', description='get layer information from the DisplayLayerProgress plugin', help='get layer information from the DisplayLayerProgress plugin')
com_layers.set_defaults(func=layers)

def gcode(args):
    command = args.command
    request = caller.post('/api/printer/command', {'command':command})
    if request != 204:
        print(colored('G-code execution failed', 'red', attrs=['bold']))
        sys.exit(1)
    sys.exit(0)

com_gcode = subparsers.add_parser('gcode', description='run gcode on printer', help='run gcode on printer')
com_gcode.add_argument('command', type=str, help='gcode command')
com_gcode.set_defaults(func=gcode)

com_print = subparsers.add_parser('print', description='print job commands', help='print job commands')
coms_print = com_print.add_subparsers()

def print_status(args):
    state = caller.getState()
    if state == 'Offline': #printer disconnected
        print(colored("Printer Disconnected", 'red', attrs=['bold']))
    elif state.startswith('Offline'): #Offline status with error message following
        print(colored("Printer Disconnected", 'red', attrs=['bold']))
        print(state)
    elif state.startswith('Error'): #Error status
        print(colored("Error", 'red', attrs=['bold']))
        print(colored("Error: ", attrs=['bold'])+state[7:])
    else:
        selectedFile = caller.getFile()
        data = caller.get("/api/job")
        data2 = caller.get("/api/printer")
        def tempPrint():
            print(colored("Extruder Temp: ", attrs=['bold']) + str(data2['temperature']['tool0']['actual'])+"°C")
            print(colored("Extruder Target: ", attrs=['bold']) + str(data2['temperature']['tool0']['target'])+"°C")
            print(colored("Bed Temp: ", attrs=['bold']) + str(data2['temperature']['bed']['actual'])+"°C")
            print(colored("Bed Target: ", attrs=['bold']) + str(data2['temperature']['bed']['target'])+"°C")
        def jobPrint():
            print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
            print(colored("Estimated Total Print Time: ", attrs=['bold']) + caller.getTotalTime())
            print(colored("Estimated Print Time Left: ", attrs=['bold']) + caller.getTimeLeft())
            print(colored("Progress: ", attrs=['bold']) + str(round(data['progress']['completion']))+"%")

        if state == 'Operational' and selectedFile:
            print(colored("Printer Operational", 'green', attrs=['bold']))
            print(colored("Loaded File: ", attrs=['bold']) + data['job']['file']['name'])
            print(colored("Estimated Print Time: ", attrs=['bold']) + caller.getTotalTime())
            tempPrint()
        elif state == 'Operational':
            print(colored("Printer Operational", 'green', attrs=['bold']))
            tempPrint()
        elif state == 'Printing':
            print(colored("Printing", 'green', attrs=['bold']))
            jobPrint()
            tempPrint()
        elif state == 'Paused':
            print(colored("Paused", 'yellow', attrs=['bold']))
            jobPrint()
            tempPrint()
        elif state == 'Pausing':
            print(colored("Pausing", 'yellow', attrs=['bold']))
            jobPrint()
            tempPrint()
        elif state == 'Cancelling':
            print(colored("Cancelling", 'red', attrs=['bold']))
            print(colored("File: ", attrs=['bold']) + data['job']['file']['name'])
            tempPrint()
        elif state == 'Finishing':
            print(colored("Finishing", 'green', attrs=['bold']))
            jobPrint()
            tempPrint()
    sys.exit(0)

com_print_status = coms_print.add_parser('status', description='view print job status', help='view print job status')
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

com_print_select = coms_print.add_parser('select', description='select file on server to load', help='select file on server to load')
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

com_print_start = coms_print.add_parser('start', description='start print job on selected file', help='start print job on selected file')
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

com_print_cancel = coms_print.add_parser('cancel', description='cancel current print job', help='cancel current print job')
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

com_print_pause = coms_print.add_parser('pause', description='pause current print job', help='pause current print job')
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

com_print_resume = coms_print.add_parser('resume', description='resume current print job', help='resume current print job')
com_print_resume.set_defaults(func=print_resume)

com_connection = subparsers.add_parser('connection', description='printer connection commands', help='printer connection commands')
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

com_connection_status = coms_connections.add_parser('status', description='get printer connection status', help='get printer connection status')
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

com_connection_connect = coms_connections.add_parser('connect', description='connect to printer', help='connect to printer')
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

com_connection_disconnect = coms_connections.add_parser('disconnect', description='disconnect from printer', help='disconnect from printer')
com_connection_disconnect.set_defaults(func=connection_disconnect)

com_temp = subparsers.add_parser('temp', description='printer temperature commands', help='printer temperature commands')
coms_temp = com_temp.add_subparsers()

def temp_status(args):
    data = caller.get("/api/printer")
    if data == 409:
        print(colored("Printer is not operational", 'red', attrs=['bold']))
        sys.exit(1)
    if isinstance(data, dict):
        print(colored("Extruder Temp: ", attrs=['bold'])+str(data['temperature']['tool0']['actual'])+"°C")
        print(colored("Extruder Target: ", attrs=['bold'])+str(data['temperature']['tool0']['target'])+"°C")
        print(colored("Bed Temp: ", attrs=['bold'])+str(data['temperature']['bed']['actual'])+"°C")
        print(colored("Bed Target: ", attrs=['bold'])+str(data['temperature']['bed']['target'])+"°C")

com_temp_status = coms_temp.add_parser('status', description='view temperature status of extruder and print bed', help='view temperature status of extruder and print bed')
com_temp_status.set_defaults(func=temp_status)

def temp_extruder(args):
    try:
        if args.temperature > int(config['print']['MaxExtruderTemp']):
            print(colored("Target temp is higher than the limit set in the configuration file", 'red', attrs=['bold']))
            sys.exit(2)
    except KeyError:
        pass
    code = caller.post("/api/printer/tool", {'command':'target','targets':{'tool0':args.temperature}})
    if code == 204:
        print(colored("Extruder temp set to " + str(args.temperature)+"°C", 'green', attrs=['bold']))
        sys.exit(0)
    elif code == 409:
        print(colored("Printer is not operational", 'red', attrs=['bold']))
        sys.exit(1)
    else:
        print(colored("Unable to change temperature", 'red', attrs=['bold']))
        sys.exit(1)

com_temp_extruder = coms_temp.add_parser('extruder', description='set extruder target temperature', help='set extruder target temperature')
com_temp_extruder.set_defaults(func=temp_extruder)
com_temp_extruder.add_argument('temperature', type=int, help='target temperature, if set to 0 the extruder will be turned off')

def temp_bed(args):
    try:
        if args.temperature > int(config['print']['MaxBedTemp']):
            print(colored("Target temp is higher than the limit set in the configuration file", 'red', attrs=['bold']))
            sys.exit(2)
    except KeyError:
        pass
    code = caller.post("/api/printer/bed", {'command':'target','target':args.temperature})
    if code == 204:
        print(colored("Bed temp set to " + str(args.temperature)+"°C", 'green', attrs=['bold']))
        sys.exit(0)
    elif code == 409:
        print(colored("Printer is not operational", 'red', attrs=['bold']))
        sys.exit(1)
    else:
        print(colored("Unable to change temperature", 'red', attrs=['bold']))
        sys.exit(1)

com_temp_bed = coms_temp.add_parser('bed', description='set print bed target temperature', help='set print bed target temperature')
com_temp_bed.set_defaults(func=temp_bed)
com_temp_bed.add_argument('temperature', type=int, help='target temperature, if set to 0 the bed will be turned off')

com_system = subparsers.add_parser('system', description='server management commands', help='server management commands')
coms_system = com_system.add_subparsers()

def system_restart(args):
    prompt = input(colored("You are restarting the server. Are you sure you wish to continue?",attrs=['bold'])+" [Y/n]: ")
    if not(prompt.lower() == "y" or prompt.lower == "yes"):
        sys.exit(0)
    code = caller.post("/api/system/commands/core/restart",{})
    if code != 204:
        print(colored("Unable to restart",'red',attrs=['bold']))
        sys.exit(1)
    else:
        print("OctoPrint is restarting")

com_system_restart = coms_system.add_parser('restart', description='restart OctoPrint server', help='restart OctoPrint server')
com_system_restart.set_defaults(func=system_restart)

def system_restart_safe(args):
    prompt = input(colored("You are restarting the server to safe mode. Are you sure you wish to continue?",attrs=['bold'])+" [Y/n]: ")
    if not(prompt.lower() == "y" or prompt.lower == "yes"):
        sys.exit(0)
    code = caller.post("/api/system/commands/core/restart_safe",{})
    if code != 204:
        print(colored("Unable to restart",'red',attrs=['bold']))
        sys.exit(1)
    else:
        print("OctoPrint is restarting to safe mode")

com_system_restart_safe = coms_system.add_parser('restart-safe', description='restart OctoPrint server to safe mode', help='restart OctoPrint server to safe mode')
com_system_restart_safe.set_defaults(func=system_restart_safe)

def system_reboot(args):
    prompt = input(colored("You are rebooting the server. Are you sure you wish to continue?",attrs=['bold'])+" [Y/n]: ")
    if not(prompt.lower() == "y" or prompt.lower == "yes"):
        sys.exit(0)
    code = caller.post("/api/system/commands/core/reboot",{})
    if code != 204:
        print(colored("Unable to reboot",'red',attrs=['bold']))
        sys.exit(1)
    else:
        print("Server is rebooting")

com_system_reboot = coms_system.add_parser('reboot', description='reboot OctoPrint server', help='reboot OctoPrint server')
com_system_reboot.set_defaults(func=system_reboot)

def system_shutdown(args):
    prompt = input(colored("You are shutting down the server. Are you sure you wish to continue?",attrs=['bold'])+" [Y/n]: ")
    if not(prompt.lower() == "y" or prompt.lower == "yes"):
        sys.exit(0)
    code = caller.post("/api/system/commands/core/shutdown",{})
    if code != 204:
        print(colored("Unable to shutdown",'red',attrs=['bold']))
        sys.exit(1)
    else:
        print("Server is shutting down")

com_system_shutdown = coms_system.add_parser('shutdown', description='shutdown OctoPrint server', help='shutdown OctoPrint server')
com_system_shutdown.set_defaults(func=system_shutdown)

com_files = subparsers.add_parser('files', description='server file management commands', help='server file management commands')
coms_files = com_files.add_subparsers()

def files_list(args):
    container = 'files'
    if args.path:
        if args.path.startswith("/"):
            args.path = args.path[1:]
        if args.path.endswith("/"):
            args.path = args.path[:-1]
        print("Listing files in "+args.path)
        container = 'children'
        data = caller.get("/api/files/local/"+args.path)
        if data == 404:
            print(colored("Folder does not exist", 'red', attrs=['bold']))
            sys.exit(1)
    else:
        data = caller.get("/api/files")
    longestName=0
    longestType=0
    folders = []
    files = []
    for i in data[container]:
        if len(i['name']) > longestName: longestName = len(i['name'])
        if len(i['type']) > longestType: longestType = len(i['type'])
        if i['type'] == 'folder':
            folders.append(i)
        else:
            files.append(i)
    print(colored("NAME", attrs=['bold']) + (" "*longestName) + colored("TYPE", attrs=['bold']) + (" "*longestType) + colored("SIZE", attrs=['bold'])) #table headings
    longestName+=4
    longestType+=4
    folders.sort(key=lambda e : e['name'])
    files.sort(key=lambda e : e['name'])
    if not args.files:
        for i in folders:
            print(i['name'] + ((longestName-len(i['name']))*" ") + i['type'] + ((longestType-len(i['type']))*" "),end='')
            try:
                if i['type'] != 'folder': print(str(round(i['size']/1048576.0,2)) + " MB")
                else: print()
            except KeyError: print()
    if not args.folders:
        for i in files:
            print(i['name'] + ((longestName-len(i['name']))*" ") + i['type'] + ((longestType-len(i['type']))*" "),end='')
            try:
                if i['type'] != 'folder': print(str(round(i['size']/1048576.0,2)) + " MB")
                else: print()
            except KeyError: print()
    if container=='files': print(colored("\nFree space: ", attrs=['bold'])+str(round(data['free']/1073741824.0,3))+" GB") #disk space
    sys.exit(0)

com_files_list = coms_files.add_parser('list', description='list files from server', help='list files from server')
com_files_list.set_defaults(func=files_list)
com_files_list.add_argument('-p', '--path', type=str, dest='path', action='store', help='path for listing files from a folder')
com_files_list_filters = com_files_list.add_mutually_exclusive_group()
com_files_list_filters.add_argument('--folders', help='show only folders', action='store_true')
com_files_list_filters.add_argument('--files', help='show only files', action='store_true')

def files_info(args):
    if args.path.startswith("/"):
        args.path = args.path[1:]
    data = caller.get("/api/files/local/"+args.path)
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

com_files_info = coms_files.add_parser('info', description='get info on a file or folder', help='get info on a file or folder')
com_files_info.set_defaults(func=files_info)
com_files_info.add_argument('path', type=str, help='path to file/folder')

def files_upload(args):
    if not os.path.exists(args.path):
        print(colored("File not found", 'red', attrs=['bold']))
        sys.exit(1)
    data = caller.fileUpload(args.path)

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

com_files_upload = coms_files.add_parser('upload', description='upload a file to the server', help='upload a file to the server')
com_files_upload.set_defaults(func=files_upload)
com_files_upload.add_argument('path', type=str, help='path to local file to upload')

opt_config = optionals.add_argument('-c', '--config', type=str, dest='config_path', action='store', help='custom path to config file')

def main():
    options = parser.parse_args()

    if options.config_path != None:
        if loadConfig(options.config_path):
            pass
        else:
            print("Configuration file is not complete or does not exist")
            sys.exit(1)
    else:
        if loadConfig(os.path.join(sys.path[0],'config.ini')):
            pass
        elif loadConfig(os.path.expanduser('~/.config/octoprint-cli.ini')):
            pass
        else:
            print("Configuration file is not complete or does not exist")
            sys.exit(1)
    init_config()

    def updateCheck():
        request = requests.get('https://api.github.com/repos/UserBlackBox/octoprint-cli/releases/latest')
        if request.status_code == 200:
            v = lambda t: tuple(map(int,t.split('.')))
            if v(request.json()['tag_name'][1:]) > v(__version__):
                print("octoprint-cli can be updated using pip")

    try:
        if config['preferences']['UpdateCheck'] == 'true':
            updateCheck()
    except KeyError:
        updateCheck()

    def nt_colored(*args, attrs=None):
        return args[0]

    global colored
    color = True #termcolor configuration
    if os.name=='nt':
        colored = nt_colored
        color = False
    try:
        if config['preferences']['FormattedText'] == "false":
            colored = nt_colored
            color = False
    except KeyError:
        pass
    if color != True:
        colored = nt_colored

    if caller.connectionTest() == False:
        print(colored("OctoPrint server cannot be reached", 'red', attrs=['bold']))
        sys.exit(1)
    if caller.authTest() == False:
        print(colored("X-API-Key is incorrect", 'red', attrs=['bold']))
        sys.exit(1)

    try:
        options.func(options)
    except AttributeError:
        print(colored("Invalid or Missing Arguments", 'red', attrs=['bold']))
        print(parser.format_help())
        sys.exit(2)

if __name__ == "__main__":
    main()