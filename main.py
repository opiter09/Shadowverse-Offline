import os
import sys
import PySimpleGUI as psg
import json
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
window = psg.Window("", layout)
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
else:
    play.playBall(realData)
