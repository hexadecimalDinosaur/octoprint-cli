import requests
from sys import stderr
from functools import lru_cache


class api:
    address = ""
    XApiKey = ""
    header = {}
    verbose = False

    def __init__(self, destination, key, verbose=False):
        """api caller constructor method"""
        self.address = destination
        self.XApiKey = key
        self.header['X-API-Key'] = key
        self.verbose = verbose

    @lru_cache
    def get(self, target):
        if self.verbose:
            print("INFO: GET request to %s" %
                  (self.address+target), file=stderr)
        request = requests.get(self.address+target, headers=self.header)
        if request.status_code != 200:
            if self.verbose:
                print("ERROR: Status code %d from request to %s" %
                      (self.address+target, request.status_code), file=stderr)
            return request.status_code
        return request.json()

    def get_cacheless(self, target):
        if self.verbose:
            print("INFO: GET request to %s" %
                  (self.address+target), file=stderr)
        request = requests.get(self.address+target, headers=self.header)
        if request.status_code != 200:
            if self.verbose:
                print("ERROR: Status code %d from request to %s" %
                      (self.address+target, request.status_code), file=stderr)
            return request.status_code
        return request.json()

    def post(self, target, data):
        request = requests.post(self.address+target,
                                headers=self.header, json=(data))
        if self.verbose:
            print("INFO: POST request to %s with data %s and return code %d" %
                  (self.address+target, data, request.status_code),
                  file=stderr)
        return request.status_code

    def connectionTest(self):
        if self.verbose:
            print("INFO: Running connection check", file=stderr)
        try:
            if isinstance(self.get("/api/version"), dict):
                return True
            else:
                return False
        except requests.ConnectionError:
            if self.verbose:
                print("ERROR: Connection check failed", file=stderr)
            return False

    def authTest(self):
        if self.verbose:
            print("INFO: Running authentication check", file=stderr)
        if isinstance(self.get("/api/job"), dict):
            return True
        else:
            if self.verbose:
                print("ERROR: Authentication check failed", file=stderr)
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
        if not time:
            return "unavailable"
        hours = int(time//3600)
        if len(str(hours)) == 1:
            hours = "0"+str(hours)
        time = time % 3600
        minutes = int(time//60)
        time = int(time % 60)
        if len(str(minutes)) == 1:
            minutes = "0"+str(minutes)
        time = int(time % 60)
        if len(str(time)) == 1:
            time = "0"+str(time)
        return str(hours)+":"+str(minutes)+":"+str(time)

    def getTotalTime(self):
        time = self.get("/api/job")['job']['estimatedPrintTime']
        if not time:
            return "unavailable"
        hours = int(time//3600)
        if len(str(hours)) == 1:
            hours = "0"+str(hours)
        time = time % 3600
        minutes = int(time//60)
        time = int(time % 60)
        if len(str(minutes)) == 1:
            minutes = "0"+str(minutes)
        return str(hours)+":"+str(minutes)

    def selectFile(self, fileName):
        return self.post("/api/files/local/"+fileName, {'command': 'select'})

    def printRequests(self, command):
        return self.post("/api/job", {'command': command})

    def pauseRequests(self, action):
        return self.post("/api/job", {'command': 'pause', 'action': action})

    def fileUpload(self, file):
        if self.verbose:
            print("INFO: Reading file %s" % (file), file=stderr)
        fle = {'file': open(file, 'rb'), 'filename': file}
        request = requests.post(
            self.address+"/api/files/local", headers=self.header, files=fle)
        if self.verbose:
            print("INFO: POST request to %s and return code %d" % (
                self.address+"/api/files/local", request.status_code),
                file=stderr)
        if request.status_code == 201:
            return request.json()
        return request.status_code
