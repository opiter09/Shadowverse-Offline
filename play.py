import os
import sys
import PySimpleGUI as psg
import json
import random
import time
import socket

first = -1
def deckImport(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive):
    file = psg.popup_get_file("Select your deck file:", file_types = [("Text Files", "*.txt")])
    if (os.path.exists(file) == False):
        file = "Deck.txt"

    f = open(file, "rt")
    deck = f.read().split("\n")
    f.close()
    
    if (len(deck) != 40):
        print("Invalid deck! Improper deck size detected!")
        return(None, None)

    bad = 0
    prev = "Neutral"
    counts = {}
    for i in range(len(deck)):
        if (bad > 0):
            break
        for card in table:
            if (card["card_name"] != None):
                if (card["card_name"].lower().replace(" ", "") == deck[i].lower().replace(" ", "")):
                    if ((prev != "Neutral") and (card["clan"] != "Neutral") and (card["clan"] != prev)):
                        bad = 1
                    else:
                        prev = card["clan"]
                        deck[i] = card["card_name"]
                        if (counts.get(deck[i]) == None):
                            counts[deck[i]] = 1
                        else:
                            counts[deck[i]] = counts[deck[i]] + 1
                    break
        if (counts.get(deck[i]) == None):
            print(deck[i])
            bad = 2
    if (bad == 1):
        print("Invalid deck! Cards of multiple classes detected!")
        return(None, None)
    elif (bad == 2):
        print("Invalid deck! Nonexistant cards detected!")
        return(None, None)
    for val in counts.values():
        if (val > 3):
            print("Invalid deck! More than three copies of a card detected!")
            return(None, None)

    random.shuffle(deck)
    global first

    if (role == "client"):
        first = int(time.time()) % 2
        while True:
            try:
                sockS.connect(theirReceive)
                sockS.sendall((json.dumps(deck) + "~~~" + str(first)).encode("UTF-8"))
                break
            except:
                print("Deck upload failed!")
                return(None)
        # print("host middle")
        sockR.listen(1)
        packet = ""
        while (packet == ""):
            # Find connections
            connection, address = sockR.accept()
            try:
                packet = connection.recv(65536).decode("UTF-8")
            except:
                connection.close()
                print("Deck download failed!")
                return(None)
        # connection.close()
    elif (role == "host"):
        sockR.listen(1)
        packet = ""
        while (packet == ""):
            # Find connections
            connection, address = sockR.accept()
            try:
                packet = connection.recv(65536).decode("UTF-8")
            except:
                connection.close()
                print("Deck download failed!")
                return(None)
        # connection.close()
        # print("client middle")
        while True:
            try:
                sockS.connect(theirReceive)
                sockS.sendall((json.dumps(deck)).encode("UTF-8"))
                break
            except:
                print("Deck upload failed!")
                return(None)

    packetDeck = json.loads(packet.split("~~~")[0])
    if (first == -1):
        first = int(packet.split("~~~")[1])
    # print(packetDeck[0]["card_name"])
    # print(deck[0]["card_name"])
    return(deck, packetDeck, connection)

def updateButtons(window, transferState, keyNames):
    for i in range(7):
        for j in range(9):
            if ((i in [1, 2, 3, 4]) and (j in [0, 1, 7, 8])):
                continue              
            else:
                if (i in [2, 3]):
                    window[keyNames[i] + str(j)].update(text = transferState[keyNames[i]][j - 2])
                elif (((i == 0) and (transferState["theirHand"][j] == "BLANK")) or ((i == 5) and (transferState["yourHand"][j] == "BLANK"))):
                    window[keyNames[i] + str(j)].update(text = "BLANK")
                else:   
                    if (i == 0):
                        if (transferState["theirHandRevealed"][j] == False):
                            window[keyNames[i] + str(j)].update(text = "UNKNOWN")
                        else:
                            window[keyNames[i] + str(j)].update(text = transferState["theirHand"][j])
                    elif (i in [1, 4]):
                        window[keyNames[i] + str(j)].update(text = str(transferState[keyNames[i].split("D")[0] + "FieldDamage"][j - 2]) + " Dmg / " \
                                                                + str(transferState[keyNames[i].split("D")[0] + "FieldCounters"][j - 2]) + " Cnt")
                    elif (i == 5):
                        window[keyNames[i] + str(j)].update(text = transferState["yourHand"][j])
    for s in [ "your", "their" ]:
        window[s + "Life"].update(text = str(transferState[s + "Life"]) + " LIFE")
        window[s + "Play"].update(text = str(transferState[s + "CurrentPlayPoints"]) + " / " + str(transferState[s + "MaxPlayPoints"]) + " PLAY")
        window[s + "Evo"].update(text = str(transferState[s + "CurrentEvoPoints"]) + " / " + str(transferState[s + "MaxEvoPoints"]) + " EVOLVE")
        window[s + "Turns"].update(text = str(transferState[s + "EvoWait"]) + " TURNS")
        window[s + "Counters"].update(text = str(transferState[s + "ClassCounters"]) + " COUNTERS")

def playBall(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive):
    # print(role)
    try:
        yourBaseDeck, theirBaseDeck, connectR = deckImport(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive)
        if (yourBaseDeck == None):
            connectR.close()
            sockR.close()
            sockS.close()
            return
    except:
        try:
            connectR.close()
        except:
            pass
        sockR.close()
        sockS.close()
        return

    global first
    trick = [ "host", "client" ]
    if (role == trick[first]):
        e = ["3", "2"]
    else:
        e = ["2", "3"]
        
    transferState = {
        "currentTurn": trick[first],
        "yourHand": yourBaseDeck[0:3] + (["BLANK"] * 6),
        "yourHandRevealed": [False] * 9,
        "yourDeck": yourBaseDeck[3:],
        "yourGraveyard": [],
        "yourBanishedZone": [],
        "yourFusedZone": [],
        "yourField": ["BLANK"] * 5,
        "yourFieldEvo": [False] * 5,
        "yourFieldDamage": [0, 0, 0, 0, 0],
        "yourFieldCounters": [0, 0, 0, 0, 0],
        "yourLife": 20,
        "yourCurrentPlayPoints": 0,
        "yourMaxPlayPoints": 0,
        "yourCurrentEvoPoints": e[1],
        "yourMaxEvoPoints": e[1],
        "yourEvoWait": 4,
        "yourClassCounters": 0,
        "theirHand": theirBaseDeck[0:3] + (["BLANK"] * 6),
        "theirHandRevealed": [False] * 9,
        "theirDeck": theirBaseDeck[3:],
        "theirGraveyard": [],
        "theirBanishedZone": [],
        "theirFusedZone": [],
        "theirField": ["BLANK"] * 5,
        "theirFieldEvo": [False] * 5,
        "theirFieldDamage": [0, 0, 0, 0, 0],
        "theirFieldCounters": [0, 0, 0, 0, 0],
        "theirLife": 20,
        "theirCurrentPlayPoints": 0,
        "theirMaxPlayPoints": 0,
        "theirCurrentEvoPoints": e[0],
        "theirMaxEvoPoints": e[0],
        "theirEvoWait": 4,
        "theirClassCounters": 0
    }
    
    layout = [[], [], [], [], [], [], []]
    keyNames = [ "theirHand", "theirDamage", "theirField", "yourField", "yourDamage", "yourHand" ]
    for i in range(7):
        for j in range(9):
            if ((i in [1, 2, 3, 4]) and (j in [0, 1, 7, 8])):
                if (i in [1, 4]):
                    layout[i] = layout[i] + [ psg.Button("", key = keyNames[i] + str(j), size = (15, 2), disabled = True) ]
                else:
                    layout[i] = layout[i] + [ psg.Button("", key = keyNames[i] + str(j), size = (15, 3), disabled = True) ]
            else:
                if (i in [2, 3]):
                    layout[i] = layout[i] + [ psg.Button("BLANK", key = keyNames[i] + str(j), size = (15, 3), enable_events = True) ]
                elif (((i == 0) and (transferState["theirHand"][j] == "BLANK")) or ((i == 5) and (transferState["yourHand"][j] == "BLANK"))):
                    layout[i] = layout[i] + [ psg.Button("BLANK", key = keyNames[i] + str(j), size = (15, 2), enable_events = True) ]
                else:   
                    if (i == 0):
                        layout[i] = layout[i] + [ psg.Button("UNKNOWN", key = keyNames[i] + str(j), size = (15, 2), enable_events = True) ]
                    elif (i in [1, 4]):
                        layout[i] = layout[i] + [ psg.Button("0 Dmg / 0 Cnt", key = keyNames[i] + str(j), size = (15, 2), enable_events = True) ]
                    elif (i == 5):
                        layout[i] = layout[i] + [ psg.Button(transferState["yourHand"][j], key = keyNames[i] + str(j), size = (15, 2),
                                                    enable_events = True) ]

    layout[0] = layout[0] + [ psg.Button("20 LIFE", key = "theirLife", size = (12, 1)), psg.Button("0 / 0 PLAY", key = "theirPlay", size = (12, 1)) ]
    layout[1] = layout[1] + [ psg.Button(e[0] + " / " + e[0] + " EVOLVE", key = "theirEvo", size = (12, 1)),
                                psg.Button("4 TURNS", key = "theirTurns", size = (12, 1)) ]
    layout[2] = layout[2] + [ psg.Button("0 COUNTERS", key = "theirCounters", size = (12, 2)),
                                psg.Button("X TIMES", key = "theirOccurances", size = (12, 2)) ]
    layout[3] = layout[3] + [ psg.Button("0 COUNTERS", key = "yourCounters", size = (12, 2)),
                                psg.Button("0 TIMES", key = "yourOccurances", size = (12, 2)) ]
    layout[4] = layout[4] + [ psg.Button(e[1] + " / " + e[1] + " EVOLVE", key = "yourEvo", size = (12, 1)),
                                psg.Button("4 TURNS", key = "yourTurns", size = (12, 1)) ]
    layout[5] = layout[5] + [ psg.Button("20 LIFE", key = "yourLife", size = (12, 1)), psg.Button("0 / 0 PLAY", key = "yourPlay", size = (12, 1)) ]
    
    subLay = [
        [ psg.Button("Receive", key = "receiveData"), psg.Button("Send", key = "sendData"), psg.Button("End Turn", key = "endTurn") ],
        [ psg.Text("Left/Only Value:"), psg.DropDown(["Nothing", "Increase", "Decrease"], key = "leftChange", default_value = "Nothing"),
            psg.Text("Right Value:"), psg.DropDown(["Nothing", "Increase", "Decrease"], key = "rightChange", default_value = "Nothing") ],
        [ psg.Text("Move Card To:  "), psg.DropDown(["Your", "Their"], key = "whoseZone", default_value = "Your"),
            psg.DropDown([ "Nowhere", "Hand", "Field", "Deck", "Graveyard", "Banish", "Fusion" ], default_value = "Nowhere", key = "moveLoc") ],
        [ psg.Text("Add"), psg.Input(key = "createCard"), psg.Text("To Your:"),
            psg.DropDown([ "Nowhere", "Hand", "Field", "Deck", "Graveyard", "Banish", "Fusion" ], default_value = "Nowhere", key = "addLoc"),
            psg.Button("Do It", key = "addButton") ],
        [ psg.Button("View Graveyard", key = "viewGrave", size = (12, 1)), psg.Button("View Banish", key = "viewBanish"),
            psg.Button("Draw Card", key = "drawCard"), psg.Button("Shuffle Deck", key = "shuffleDeck") ],
        [ psg.Text("Randomly Choose A(n)"), psg.DropDown(["Follower", "Amulet", "Spell"], key = "randomType", default_value = "Follower"),
            psg.Text("From Your"),
            psg.DropDown([ "Nowhere", "Hand", "Field", "Deck", "Graveyard", "Banish", "Fusion" ], default_value = "Nowhere", key = "chooseLoc"),
            psg.Text("Whose Cost Is:"), psg.DropDown(["Nothing", "Greater Than", "Less Than", "Equal To"], default_value = "Nothing", key = "compare"),
            psg.DropDown([str(x) for x in list(range(21))], default_value = "0", key = "compVal"), psg.Button("Do It", key = "rollDice") ]
    ]
    layout[6] = [
        psg.Column([[psg.Image("blank_card.png", key = "yourCardImage")]]),
        psg.Column(subLay),
        psg.Column([[psg.Image("blank_card.png", key = "theiCardImage")]]),
    ]

    window = psg.Window("", layout, grab_anywhere = True, resizable = True, auto_size_buttons = False)
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
            connectR.close()
            sockS.close()
            sockR.close()
            break

        try:
            longName = "results/" + window[event].get_text().replace(" ", "_")
            if (os.path.exists(longName + "_base.png")):
                window[event[0:4] + "CardImage"].update(filename = longName + "_base.png")
                window.refresh()
                if ((longName.endswith("EVOLVED") == True) and (os.path.exists(longName.split("_EVOLVED")[0] + "_evolved.png"))):
                    window[event[0:4] + "CardImage"].update(filename = longName.split("_EVOLVED")[0].replace(" ", "_") + "_evolved.png")
                    window.refresh()            
        except:
            pass

        if (event == "sendData"):
            while True:
                try:
                    sockS.sendall((json.dumps(transferState).encode("UTF-8")))
                    break
                except:
                    psg.popup("Data transfer failed!")
                    break
        elif (event == "receiveData"):
            packet = ""
            while (packet == ""):
                try:
                    packet = connectR.recv(65536).decode("UTF-8")
                except:
                    psg.popup("Data transfer failed!")
                    break
            if (packet != ""):
                transferState = json.loads(packet.replace("\"your", "xkcdxkcd").replace("\"their", "\"your").replace("xkcdxkcd", "\"their"))   
                updateButtons(window, transferState, keyNames)
        elif (event == "endTurn"):
            transferState["currentTurn"] = trick[int(not trick.index(transferState["currentTurn"]))]

    window.close()
    connectR.close()
    sockR.close()
    sockS.close()