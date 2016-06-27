import time
import random
import string
import os
import json
from slackclient import SlackClient

token = input("Enter token: ")
sc = SlackClient(token);

msg = ":calen:"
currentChan = ""
responsePath = "./responses.txt"

def generateResponseFile():
    if os.path.isfile(responsePath) == False:
        f = open(responsePath,'w+')
        text = "{\"!meme\": [\":calen:\",\":dong:\",\":atom:\"]}"
        f.write(text);
        f.close()

def getResponses():
    f = open(responsePath,'r+');
    js = json.loads(f.read())
    f.close()
    return js;

def responseExists(command): #check if the JSON has a specified command in it
    f = open(responsePath,'r+');
    js = json.loads(f.read())
    if command in js.keys():
        f.close()
        return True
    f.close()
    return False 

def addCommand(text):
    f = open(responsePath,'r');
    js = json.loads(f.read())
    wordList = text.split("/",1)
    # catch improper syntax
    if (len(wordList) < 2 or len(wordList[0].strip()) == 0 or len(wordList[1].strip()) == 0):
        sc.api_call("chat.postMessage", channel=currentChan, text="Usage: ```!addcommand (COMMAND) / (RESPONSE)```")
    else:
        command = wordList[0].strip()
        response = wordList[1].strip()
        if responseExists(command) == False:
            js[command] = [response]
            f.close()
            f = open(responsePath,'w');
            json.dump(js,f)
            sc.api_call("chat.postMessage", channel=currentChan, text="Command added.")
        else:
            sc.api_call("chat.postMessage", channel=currentChan, text="Command already exists.")
    f.close()

def addResponse(text):
    f = open(responsePath,'r+');
    js = json.loads(f.read())
    wordList = text.split("/",1)
    command = wordList[0].strip()
    response = wordList[1].strip()
    if responseExists(command) == True:
        js[command].append(response)
        f.close()
        f = open(responsePath,'w');
        json.dump(js,f)
        sc.api_call("chat.postMessage", channel=currentChan, text="Command updated.")
    f.close()
        
def sayResponse(command):
    f = open(responsePath,'r+');
    js = json.loads(f.read())
    if command in js.keys():
        response = random.choice(js[command])
        sc.api_call("chat.postMessage", channel=currentChan, text=response)
        f.close()

def readText(text): #read text and determine if it's a command. If it is, process the command accordingly. Takes a string.   
    if "!addcommand" in text.lower():
        location = text.find("!addcommand") + len("!addcommand") + 1
        addCommand(text[location:])
    elif "!addresponse" in text.lower():
        location = text.find("!addresponse") + len("!addresponse") + 1
        addResponse(text[location:])
    #check for user-defined responses
    else:
        f = open(responsePath,'r');
        js = json.loads(f.read())
        for command in js.keys():
            if command.lower() in text.lower():
                sayResponse(command)

if sc.rtm_connect():
    generateResponseFile();
    while True: #basic bot runtime loop to read commands
        newEvents = sc.rtm_read()
        for event in newEvents:
            print(event)
            if "type" in event:
                if event["type"] == "message" and "text" in event:
                    message = event["text"]
                    currentChan = event["channel"]
                    readText(message);
            
else:
    print ("Connection Failed.")


    
