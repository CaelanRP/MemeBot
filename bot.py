import time
import random
import string
import os
import json
from slackclient import SlackClient

token = input("Enter token: ")
sc = SlackClient(token);

currentChan = ""
responsePath = "./config.txt"

def checkResponseFile():
    if os.path.isfile(responsePath) == False:
        f = open(responsePath,'w+')
        text = "{\"commands\":[{\"name\":\"!hello\", \"responses\":[\"Hi!\"]}]}"
        f.write(text);
        f.close()

def getConfig():
    f = open(responsePath,'r+');
    js = json.loads(f.read())
    f.close()
    return js;

# returns the map for a command with given name
def getResponseMap(name):
    js = getConfig()
    for commMap in js["commands"]:
        if commMap["name"] == name:
            return commMap 

def responseExists(name): #check if the JSON has a specified command in it
    js = getConfig()
    for command in js["commands"]:
        if command["name"] == name:
            return True
    return False 

# parses input to add a new user-defined command, as well as an initial response to it.
def addCommand(text):
    f = open(responsePath,'r');
    js = json.loads(f.read())
    wordList = text.split("//",1)
    # catch improper syntax
    if (len(wordList) < 2 or len(wordList[0].strip()) == 0 or len(wordList[1].strip()) == 0):
        sc.api_call("chat.postMessage", channel=currentChan, text="Usage: ```!addcommand (COMMAND) // (RESPONSE)```")
    else:
        command = wordList[0].strip()
        response = wordList[1].strip()
        if responseExists(command) == False:
            newDict = dict()
            newDict["name"] = command
            newDict["responses"] = [response]
            js["commands"].append(newDict)
            f.close()
            f = open(responsePath,'w');
            json.dump(js,f)
            sc.api_call("chat.postMessage", channel=currentChan, text="Command added.")
        else:
            sc.api_call("chat.postMessage", channel=currentChan, text="Command already exists.")
    f.close()

# parses input to add a new user-defined response to an existing command.
def addResponse(text):
    f = open(responsePath,'r+');
    js = json.loads(f.read())
    wordList = text.split("//",1)
    command = wordList[0].strip()
    response = wordList[1].strip()
    print(command)
    if responseExists(command) == True:
        print (getResponseMap(command))
        print (response)
        js["commands"][js["commands"].index(getResponseMap(command))]["responses"].append(response)
        f.close()
        f = open(responsePath,'w');
        json.dump(js,f)
        sc.api_call("chat.postMessage", channel=currentChan, text="Command updated.")
    f.close()

#Lists a set of responses for a given command
def listResponses(text):
    text = text.strip()
    js = getConfig()
    command = None
    for i in range(1,len(text)+1):
        if responseExists(text[:i]):
            command = text[:i]
            break
    if command == None:
        sc.api_call("chat.postMessage", channel=currentChan, text="Command \"" + text + "\" does not exist.")
        return
    post = "Possible responses for \"" + command + "\":\n"
    for response in getResponseMap(command)["responses"]:
        post += response + "\n"
    sc.api_call("chat.postMessage", channel=currentChan, text=post)
    
def sayResponse(command):
    js = getConfig()
    if responseExists(command):
        response = random.choice(getResponseMap(command)["responses"])
        sc.api_call("chat.postMessage", channel=currentChan, text=response)

def readText(text): #read text and determine if it's a command. If it is, process the command accordingly. Takes a string.   
    if "!help" in text.lower():
        userHelp()
    elif "!addcommand" in text.lower():
        location = text.find("!addcommand") + len("!addcommand") + 1
        addCommand(text[location:])
    elif "!addresponse" in text.lower():
        location = text.find("!addresponse") + len("!addresponse") + 1
        addResponse(text[location:])
    elif "!listresponses" in text.lower():
        location = text.find("!listresponses") + len("!listresponses") + 1
        listResponses(text[location:])
    #check for user-defined responses
    else:
        f = open(responsePath,'r');
        js = json.loads(f.read())
        for command in js["commands"]:
            if command["name"].lower() in text.lower():
                sayResponse(command["name"])
                break
        f.close

def userHelp():
    f = open("./botcommands.txt")
    sc.api_call("chat.postMessage", channel=currentChan, text=f.read())

if sc.rtm_connect():
    checkResponseFile();
    while True: #basic bot runtime loop to read commands
        newEvents = sc.rtm_read()
        for event in newEvents:
            print(event)
            if "type" in event:
                if event["type"] == "message" and "text" in event:
                    # Prevent commands from triggering on stuff that isn't a user mssage to the channel
                    if ("subtype" in event) == False:
                        message = event["text"]
                        currentChan = event["channel"]
                        readText(message);
            
else:
    print ("Connection Failed.")


    
