#!/usr/bin/python3
# class to make the requests
import requests
import json

class api:
    address = ""
    XapiKey = ""
    header = {'Content-Type': 'application/json'}

    def __init__(self, key, destination):
        self.address = destination
        self.XapiKey = key
        self.header['X-API-Key']=key
    
    def get(self, target):
        request = requests.get(self.address+target, headers=self.header)
        if request.status_code != 200:
            return request.status_code
        return request.json()
    
    def post(self, target, data):
        request = requests.post(self.address+target, headers=self.header, data=json.dumps(data))
        return request.status_code

    def connectionTest(self):
        try:
            if type(self.get("/api/version")) is dict:
                return True
            else:
                return False
        except requests.ConnectionError:
            return False
    
    def authTest(self):
        if type(self.get("/api/job")) is dict:
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


