import os
import sys
import PySimpleGUI as psg
import json
import random

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
                        deck[i] = card
                    break
        if (type(deck[i]) == str):
            print(deck[i])
            bad = 2
    if (bad == 1):
        print("Invalid deck! Cards of multiple classes detected!")
        return(None, None)
    elif (bad == 2):
        print("Invalid deck! Nonexistant cards detected!")
        return(None, None)  
    random.shuffle(deck)

    if (role == "host"):
        while True:
            try:
                sockS.connect(theirReceive)
                sockS.sendall(json.dumps(deck).encode("UTF-8"))
                break
            except:
                print("Deck upload failed!")
                return(None, None)
        # print("host middle")
        sockR.listen(1)
        packet = ""
        while (packet == ""):
            # Find connections
            connection, address = sockR.accept()
            try:
                packet = connection.recv(262144).decode("UTF-8")
            except:
                connection.close()
                print("Deck download failed!")
                return(None, None)
        connection.close()
    elif (role == "client"):
        sockR.listen(1)
        packet = ""
        while (packet == ""):
            # Find connections
            connection, address = sockR.accept()
            try:
                packet = connection.recv(262144).decode("UTF-8")
            except:
                connection.close()
                print("Deck download failed!")
                return(None, None)
        connection.close()
        # print("client middle")
        while True:
            try:
                sockS.connect(theirReceive)
                sockS.sendall(json.dumps(deck).encode("UTF-8"))
                break
            except:
                print("Deck upload failed!")
                return(None, None)

    packet = json.loads(packet)
    # print(packet[0]["card_name"])
    # print(deck[0]["card_name"])
    return(deck, packet)

def playBall(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive):
    # print(role)
    if (role == "host"):
        deckH, deckC = deckImport(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive)
    elif (role == "client"):
        deckC, deckH = deckImport(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive)
    if (deckH == None):
        return
        
    layout = [[], [], [], [], [], [], []]
    keyNames = [ "oppnHand", "oppnField", "yourField", "yourHand" ]
    for i in range(7):
        if (i in [0, 2, 4, 6]):
            for j in range(5):
                layout[i] = layout[i] + [ psg.Button("BLANK " + keyNames[i // 2], key = keyNames[i // 2] + str(j)) ]
        
    window = psg.Window("", layout, grab_anywhere = True, resizable = True)
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
            break
    window.close()