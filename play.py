import os
import sys
import PySimpleGUI as psg
import json
import random
import time

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
    
    deckIndices = list(range(40))
    random.shuffle(deckIndices)
    global first

    if (role == "host"):
        first = int(time.time()) % 2
        while True:
            try:
                sockS.connect(theirReceive)
                sockS.sendall((json.dumps(deck) + "~~~" + json.dumps(deckIndices) + "~~~" + str(first)).encode("UTF-8"))
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
                packet = connection.recv(262144).decode("UTF-8")
            except:
                connection.close()
                print("Deck download failed!")
                return(None)
        # connection.close()
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
                return(None)
        # connection.close()
        # print("client middle")
        while True:
            try:
                sockS.connect(theirReceive)
                sockS.sendall((json.dumps(deck) + "~~~" + json.dumps(deckIndices)).encode("UTF-8"))
                break
            except:
                print("Deck upload failed!")
                return(None)

    packetDeck = json.loads(packet.split("~~~")[0])
    packetIndices = json.loads(packet.split("~~~")[1])
    if (first == -1):
        first = int(packet.split("~~~")[2])
    # print(packetDeck[0]["card_name"])
    # print(deck[0]["card_name"])
    return(deck, deckIndices, packetDeck, packetIndices, connection)

def playBall(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive):
    # print(role)
    yourDeckBase, yourDeck, theirDeckBase, theirDeck, connectR = deckImport(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive)
    if (yourDeck == None):
        return
    
    yourHand = yourDeck[0:3] + ([-1] * 6)
    yourDeck = yourDeck[3:]
    theirHand = theirDeck[0:3] + ([-1] * 6)
    theirDeck = theirDeck[3:]
    
    layout = [[], [], [], [], []]
    keyNames = [ "oppHand", "oppField", "yourField", "yourHand" ]
    for i in range(4):
        for j in range(9):
            if ((i in [1, 2]) and (j in [0, 1, 7, 8])):
                layout[i] = layout[i] + [ psg.Button("", key = keyNames[i] + str(j), size = (15, 3), disabled = True) ]
            else:
                if ((i in [1, 2]) or ((i == 0) and (theirHand[j] == -1)) or ((i == 3) and (yourHand[j] == -1))):
                    layout[i] = layout[i] + [ psg.Button("BLANK", key = keyNames[i] + str(j), size = (15, 3), enable_events = True) ]
                else:   
                    if (i == 0):
                        layout[i] = layout[i] + [ psg.Button("UNKNOWN", key = keyNames[i] + str(j), size = (15, 3), enable_events = True) ]
                    elif (i == 3):
                        layout[i] = layout[i] + [ psg.Button(yourDeckBase[yourHand[j]]["card_name"], key = keyNames[i] + str(j), size = (15, 3),
                                                    enable_events = True) ]
    global first
    trick = [ "host", "client" ]
    currentTurn = trick[first]
    if (role == currentTurn):
        e = ["3", "2"]
    else:
        e = ["2", "3"]
    layout[0] = layout[0] + [ psg.Button("20 LIFE", key = "oppLife", size = (12, 1)), psg.Button("0 / 0 PLAY", key = "oppPlay", size = (12, 1)) ]
    layout[1] = layout[1] + [ psg.Button(e[0] + " EVOLVE", key = "oppEvo", size = (12, 1)), psg.Button("4 TURNS", key = "oppTurns", size = (12, 1)) ]
    layout[2] = layout[2] + [ psg.Button(e[1] + " EVOLVE", key = "yourEvo", size = (12, 1)), psg.Button("4 TURNS", key = "youtTurns", size = (12, 1)) ]
    layout[3] = layout[3] + [ psg.Button("20 LIFE", key = "yourLife", size = (12, 1)), psg.Button("0 / 0 PLAY", key = "yourPlay", size = (12, 1)) ]
    layout[4] = [psg.Image("blank_card.png", key = "cardImage"), psg.Button("0 Class Counter", key = "classCounter", size = (20, 1))]

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
            if (os.path.exists("results/" + window[event].get_text().replace(" ", "_") + "_base.png")):
                window["cardImage"].update(filename = "results/" + window[event].get_text().replace(" ", "_") + "_base.png", visible = True)
                window.refresh()
            else:
                window["cardImage"].update(filename = "blank_card.png")
                window.refresh()
        except:
            window["cardImage"].update(filename = "blank_card.png")
            window.refresh()
    window.close()