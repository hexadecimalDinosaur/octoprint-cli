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
        return self.get("/api/job")['progress']['printTimeLeft']
    
    def getTotalTime(self):
        return self.get("/api/job")['job']['estimatedTotalTime']


