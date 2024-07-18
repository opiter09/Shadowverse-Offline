import os
import sys
import FreeSimpleGUI as psg
import json
import subprocess
import socket
import combine
import search
import play

if (len(sys.argv) < 2):
    for root, dirs, files in os.walk("./"):
        for file in files:
            if (file.endswith(".json") == True):
                reading = open(file, "rt")
                break
else:
    reading = open(sys.argv[1], "rt")

data = json.load(reading)
if (type(data) == dict):
    if (data.get("cards") != None):
        data = data["cards"]
realData = []
for card in data:
    if ((card.get("rarity") == None) or (card["rarity"] == None) or (card.get("card_name") == None) or (card["card_name"] == None)):
        continue
    else:
        realData.append(card)

combine.createImages(realData)

result = ""
layout = [ [ psg.Text("Choose an application:") ], [ psg.Button("Search"), psg.Button("Play") ] ]
window = psg.Window("", layout, grab_anywhere = True)
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
        break
    elif (event == "Search"):
        result = "search"
        break
    elif (event == "Play"):
        result = "play"
        break
window.close()

if (result == "search"):
    search.searchWindow(realData)
elif (result == "play"):
    result2 = ""
    layout = [ [ psg.Text("Choose a role:") ], [ psg.Button("Host"), psg.Button("Client") ] ]
    window = psg.Window("", layout, grab_anywhere = True)
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
            break
        elif (event == "Host"):
            result2 = "host"
            break
        elif (event == "Client"):
            result2 = "client"
            break
    window.close()
    
    if (result2 != ""):
        yourAddress = psg.popup_get_text("Enter your IPv4 Address:", grab_anywhere = True)
        if (yourAddress != None):
            if (yourAddress == ""):
                file = open("IPv4.txt", "rt")
                yourAddress = file.read().split("\n")[0]
                file.close()
            theirAddress = psg.popup_get_text("Enter the other person's IPv4 Address:", grab_anywhere = True)
            if (theirAddress != None):
                if (theirAddress == ""):
                    file = open("IPv4.txt", "rt")
                    theirAddress = file.read().split("\n")[1]
                    file.close()
                sockS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sockR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if (result2 == "host"):
                    yourSend = (yourAddress, 10000)
                    yourReceive = (yourAddress, 10001)
                    theirSend = (theirAddress, 8080)
                    theirReceive = (theirAddress, 8081)
                elif (result2 == "client"):
                    yourSend = (yourAddress, 8080)
                    yourReceive = (yourAddress, 8081)
                    theirSend = (theirAddress, 10000)
                    theirReceive = (theirAddress, 10001)
                sockS.bind(yourSend)
                sockR.bind(yourReceive)
                play.playBall(realData, result2, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive)
