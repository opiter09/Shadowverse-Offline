import os
import sys
import FreeSimpleGUI as psg
import json
import random
import time
import socket

first = -1
def deckImport(table, role, sockS, sockR, yourSend, yourReceive, theirSend, theirReceive):
    file = psg.popup_get_file("Select your deck file:", file_types = [("Text Files", "*.txt")], grab_anywhere = True)
    if (file == None):
        return(None)
    elif (os.path.exists(file) == False):
        file = "Deck.txt"
    
    f = open(file, "rt")
    deck = f.read().split("\n")
    f.close()
    
    if (len(deck) != 40):
        print("Invalid deck! Improper deck size detected!")
        return(None)

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
        return(None)
    elif (bad == 2):
        print("Invalid deck! Nonexistant cards detected!")
        return(None)
    for val in counts.values():
        if (val > 3):
            print("Invalid deck! More than three copies of a card detected!")
            return(None)

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
        sockR.listen()
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
        sockR.listen()
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
                    if (i == 0):
                        transferState["theirHandRevealed"][j] = False
                    else:
                        transferState["yourHandRevealed"][j] = False
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
    window["yourOccurences"].update(text = str(transferState["yourOccurences"]) + " TIMES")

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
        e = [3, 2]
    else:
        e = [2, 3]
        
    transferState = {
        "yourHand": yourBaseDeck[0:3] + (["BLANK"] * 6),
        "yourHandRevealed": [False] * 9,
        "yourDeck": yourBaseDeck[3:],
        "yourGraveyard": [],
        "yourBanish": [],
        "yourFusion": [],
        "yourField": ["BLANK"] * 5,
        "yourFieldEvo": [False] * 5,
        "yourFieldDamage": [0, 0, 0, 0, 0],
        "yourFieldCounters": [0, 0, 0, 0, 0],
        "yourLife": 20,
        "yourCurrentPlayPoints": 0,
        "yourMaxPlayPoints": 0,
        "yourCurrentEvoPoints": 0,
        "yourMaxEvoPoints": e[1],
        "yourEvoWait": 4,
        "yourClassCounters": 0,
        "yourOccurences": 0,
        "theirHand": theirBaseDeck[0:3] + (["BLANK"] * 6),
        "theirHandRevealed": [False] * 9,
        "theirDeck": theirBaseDeck[3:],
        "theirGraveyard": [],
        "theirBanish": [],
        "theirFusion": [],
        "theirField": ["BLANK"] * 5,
        "theirFieldEvo": [False] * 5,
        "theirFieldDamage": [0, 0, 0, 0, 0],
        "theirFieldCounters": [0, 0, 0, 0, 0],
        "theirLife": 20,
        "theirCurrentPlayPoints": 0,
        "theirMaxPlayPoints": 0,
        "theirCurrentEvoPoints": 0,
        "theirMaxEvoPoints": e[0],
        "theirEvoWait": 4,
        "theirClassCounters": 0,
        "theirOccurences": 0
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
                        layout[i] = layout[i] + [ psg.Button("UNKOWN", key = keyNames[i] + str(j), size = (15, 2), enable_events = True) ]
                    elif (i in [1, 4]):
                        layout[i] = layout[i] + [ psg.Button("0 Dmg / 0 Cnt", key = keyNames[i] + str(j), size = (15, 2), enable_events = True) ]
                    elif (i == 5):
                        layout[i] = layout[i] + [ psg.Button(transferState["yourHand"][j], key = keyNames[i] + str(j), size = (15, 2),
                                                    enable_events = True) ]

    layout[0] = layout[0] + [ psg.Button("20 LIFE", key = "theirLife", size = (12, 1)), psg.Button("0 / 0 PLAY", key = "theirPlay", size = (12, 1)) ]
    layout[1] = layout[1] + [ psg.Button("0 / " + str(e[0]) + " EVOLVE", key = "theirEvo", size = (12, 1)),
                                psg.Button("4 TURNS", key = "theirTurns", size = (12, 1)) ]
    layout[2] = layout[2] + [ psg.Button("0 COUNTERS", key = "theirCounters", size = (12, 2)),
                                psg.Button("X TIMES", key = "theirOccurences", size = (12, 2)) ]
    layout[3] = layout[3] + [ psg.Button("0 COUNTERS", key = "yourCounters", size = (12, 2)),
                                psg.Button("0 TIMES", key = "yourOccurences", size = (12, 2)) ]
    layout[4] = layout[4] + [ psg.Button("0 / " + str(e[1]) + " EVOLVE", key = "yourEvo", size = (12, 1)),
                                psg.Button("4 TURNS", key = "yourTurns", size = (12, 1)) ]
    layout[5] = layout[5] + [ psg.Button("20 LIFE", key = "yourLife", size = (12, 1)), psg.Button("0 / 0 PLAY", key = "yourPlay", size = (12, 1)) ]
    
    subLay = [
        [ psg.Button("Receive", key = "receiveData"), psg.Button("Send", key = "sendData") ],
        [ psg.Text("Choose To"), psg.DropDown(["Reveal", "Unreveal", "Evolve", "Unevolve"], key = "flipChoice", default_value = "Reveal"),
            psg.Text("Card #"), psg.DropDown([str(x) for x in range(1, 10)], key = "flipNum", default_value = "1"), psg.Text("From Your Hand/Field"),
            psg.Button("Do It", key = "flipButton") ],
        [ psg.DropDown(["Increase", "Decrease"], key = "modifyDir", default_value = "Increase"), psg.Text("The"),
            psg.DropDown(["Left/Only Value", "Right/Only Value"], key = "modifySide", default_value = "Left/Only Value"), psg.Text("Of Your"),
            psg.DropDown(["Life", "Play Points", "Evo Points", "Evo Turns", "Counters", "Occurences", "Field 1", "Field 2", "Field 3", "Field 4",
                "Field 5"], key = "modifyChoice", default_value = "Life"),
            psg.Button("Do It", key = "modifyButton") ],
        [ psg.Text("Move"), psg.Input(size = (24, 1), key = "moveCard"), psg.Text("From Your"),
            psg.DropDown(["Hand", "Field", "Deck", "Graveyard", "Banish", "Fusion"], default_value = "Hand", key = "moveLocOut"),
            psg.Text("To"), psg.DropDown(["Your", "Their"], key = "moveWhoseZone", default_value = "Your"),
            psg.DropDown(["Hand", "Field", "Deck", "Graveyard", "Banish", "Fusion", "Deletion"], default_value = "Hand", key = "moveLocIn"),
            psg.Button("Do It", key = "moveButton") ],
        [ psg.Text("Add"), psg.Input(size = (33, 1), key = "createCard"), psg.Text("To"),
            psg.DropDown(["Your", "Their"], key = "addWhoseZone", default_value = "Your"),
            psg.DropDown(["Hand", "Field", "Deck", "Graveyard", "Banish", "Fusion"], default_value = "Hand", key = "addLoc"),
            psg.Button("Do It", key = "addButton") ],
        [ psg.Button("View Graveyard", key = "viewGraveyard", size = (12, 1)), psg.Button("View Banish", key = "viewBanish"),
            psg.Button("View Deck", key = "viewDeck"), psg.Button("Draw Card", key = "drawCard"), psg.Button("Shuffle Deck", key = "shuffleDeck") ],
        [ psg.Text("Count The"), psg.DropDown(["Cards", "Followers", "Amulets", "Spells"], key = "countType", default_value = "Cards"),
            psg.Text("In"), psg.DropDown(["Your", "Their"], default_value = "Your", key = "countWhoseZone"),
            psg.DropDown(["Hand", "Field", "Deck", "Graveyard", "Banish", "Fusion"], default_value = "Hand", key = "countLoc"),
            psg.Text("With Cost"), psg.DropDown(["Greater Than", "Less Than", "Equal To"], default_value = "Greater Than", key = "countCompare"),
            psg.Input(size = (3, 1), key = "countCNum", default_text = "0"), psg.Button("Do It", key = "countButton") ],
        [ psg.Text("Choose A(n)"), psg.DropDown(["Card", "Follower", "Amulet", "Spell"], key = "randomType", default_value = "Card"),
            psg.Text("From"), psg.DropDown(["Your", "Their"], default_value = "Your", key = "randomWhoseZone"),
            psg.DropDown(["Hand", "Field", "Deck", "Graveyard", "Banish", "Fusion"], default_value = "Hand", key = "randomLoc"),
            psg.Text("With Cost"), psg.DropDown(["Greater Than", "Less Than", "Equal To"], default_value = "Greater Than", key = "randomCompare"),
            psg.Input(size = (3, 1), key = "randomCNum", default_text = "0"), psg.Button("Do It", key = "randomButton") ]
    ]
    layout[6] = [
        psg.Column([[psg.Image("blank_card.png", key = "yourCardImage")]]),
        psg.Column(subLay),
        psg.Column([[psg.Image("blank_card.png", key = "theiCardImage")]]),
    ]

    window = psg.Window("", layout, grab_anywhere = True, resizable = True, auto_size_buttons = False)
    window2 = ""
    while True:
        static = 0
        event, values = window.read()
        # See if user wants to quit or window was closed
        if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
            connectR.close()
            sockS.close()
            sockR.close()
            break

        try:
            longName = "results/" + window[event].get_text().replace(" ", "_").replace("//", "~")
            if (os.path.exists(longName + "_base.png") == True):
                window[event[0:4] + "CardImage"].update(filename = longName + "_base.png")
                window.refresh()
            elif ((longName.endswith("EVOLVED") == True) and (os.path.exists(longName.split("_EVOLVED")[0] + "_evolved.png"))):
                window[event[0:4] + "CardImage"].update(filename = longName.split("_EVOLVED")[0].replace(" ", "_").replace("//", "~") \
                    + "_evolved.png")
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
                try:
                    transferState = json.loads(packet.replace("\"your", "xkcdxkcd").replace("\"their", "\"your").replace("xkcdxkcd", "\"their"))
                except:
                    psg.popup("State data too large!")
        elif (event == "flipButton"):
            if (values["flipChoice"] == "Reveal"):
                transferState["yourHandRevealed"][int(values["flipNum"]) - 1] = True
            elif (values["flipChoice"] == "Unreveal"):
                transferState["yourHandRevealed"][int(values["flipNum"]) - 1] = False
            elif (values["flipChoice"] == "Evolve"):
                if (values["flipNum"] in ["6", "7", "8", "9"]):
                    psg.popup("There are only five battlefield slots!")
                else:
                    string = transferState["yourField"][int(values["flipNum"]) - 1]
                    if (string != "BLANK"):
                        transferState["yourField"][int(values["flipNum"]) - 1] = string.split(" EVOLVED")[0] + " EVOLVED"
            elif (values["flipChoice"] == "Unevolve"):
                if (values["flipNum"] in ["6", "7", "8", "9"]):
                    psg.popup("There are only five battlefield slots!")
                else:
                    string = transferState["yourField"][int(values["flipNum"]) - 1]
                    if (string != "BLANK"):
                        transferState["yourField"][int(values["flipNum"]) - 1] = string.split(" EVOLVED")[0]
        elif (event == "modifyButton"):
            mapping = {
                "Life": ["yourLife", "yourLife"],
                "Play Points": ["yourCurrentPlayPoints", "yourMaxPlayPoints"],
                "Evo Points": ["yourCurrentEvoPoints", "yourMaxEvoPoints"],
                "Evo Turns": ["yourEvoWait", "yourEvoWait"],
                "Counters": ["yourClassCounters", "yourClassCounters"],
                "Occurences": ["yourOccurences", "yourOccurences"],
                "Field 1": ["yourFieldDamage", "yourFieldCounters"],
                "Field 2": ["yourFieldDamage", "yourFieldCounters"],
                "Field 3": ["yourFieldDamage", "yourFieldCounters"],
                "Field 4": ["yourFieldDamage", "yourFieldCounters"],
                "Field 5": ["yourFieldDamage", "yourFieldCounters"]
            }
            side = (["Left/Only Value", "Right/Only Value"]).index(values["modifySide"])
            if (values["modifyChoice"].startswith("Field") == True):
                i = int(values["modifyChoice"][-1]) - 1
                if (values["modifyDir"] == "Increase"):
                    transferState[mapping[values["modifyChoice"]][side]][i] = transferState[mapping[values["modifyChoice"]][side]][i] + 1
                else:
                    transferState[mapping[values["modifyChoice"]][side]][i] = max(0, transferState[mapping[values["modifyChoice"]][side]][i] - 1)
            else:
                if (values["modifyDir"] == "Increase"):
                    transferState[mapping[values["modifyChoice"]][side]] = transferState[mapping[values["modifyChoice"]][side]] + 1
                else:
                    transferState[mapping[values["modifyChoice"]][side]] = max(0, transferState[mapping[values["modifyChoice"]][side]] - 1)
        elif (event == "moveButton"):
            locOut = "your" + values["moveLocOut"]
            locIn = values["moveWhoseZone"].lower() + values["moveLocIn"]
            if (values["moveCard"] not in transferState[locOut]):
                psg.popup("No copies of that card are in that zone!")
                continue
            elif ((values["moveLocIn"] in ["Hand", "Field"]) and ("BLANK" not in transferState[locIn])):
                psg.popup("This zone is full! You may need to send the card to Deletion instead!")
                continue
            for i in range(len(transferState[locOut])):
                if (transferState[locOut][i] == values["moveCard"]):
                    if (locOut in ["yourHand", "yourField"]):
                        transferState[locOut] = transferState[locOut][0:i] + transferState[locOut][(i + 1):] + ["BLANK"]
                        if (locOut == "yourHand"):
                            before = transferState["yourHandRevealed"][0:i].copy()
                            after = transferState["yourHandRevealed"][(i + 1):].copy()
                            transferState["yourHandRevealed"] = before + after + [False]
                        break
                    else:
                        transferState[locOut].remove(transferState[locOut][i])
                        break
            if (values["moveLocIn"] != "Deletion"):
                if (values["moveLocIn"] in ["Hand", "Field"]):
                    transferState[locIn] = [values["moveCard"]] + transferState[locIn][0:-1]
                    if (values["moveLocIn"] == "Hand"):
                        rev = transferState[values["moveWhoseZone"].lower() + "HandRevealed"][0:-1].copy()
                        transferState[values["moveWhoseZone"].lower() + "HandRevealed"] = [False] + rev
                else:
                    transferState[locIn] = [values["moveCard"]] + transferState[locIn]
        elif (event == "addButton"):
            if (os.path.exists("results/" + values["createCard"].replace(" ", "_").replace("//", "~") + "_base.png") == False):
                psg.popup("This is not the name of a real card!")
                continue
            locIn = values["addWhoseZone"].lower() + values["addLoc"]
            if (values["addLoc"] in ["Hand", "Field"]):
                if ("BLANK" not in transferState[locIn]):
                    psg.popup("This zone is full! You may need to ignore the addition!")
                else:
                    transferState[locIn] = [values["createCard"]] + transferState[locIn][0:-1]
                    if (values["addLoc"] == "Hand"):
                        rev = transferState[values["addWhoseZone"].lower() + "HandRevealed"][0:-1].copy()
                        transferState[values["addWhoseZone"].lower() + "HandRevealed"] = [False] + rev
            else:
                transferState[locIn] = [values["createCard"]] + transferState[locIn]
        elif (event in ["viewGraveyard", "viewDeck", "viewBanish"]):
            layout2 = [[], [], [], [], [], [], [], [], [], []]
            count = -1
            copied = transferState["your" + event[4:]].copy()
            if (event == "viewDeck"):
                random.shuffle(copied)
            for name in copied:
                count = count + 1
                layout2[count // 5].append(psg.Button(name, size = (15, 2)))                
            window2 = psg.Window("", layout2, grab_anywhere = True, auto_size_buttons = False, keep_on_top = True)           
        elif (event == "drawCard"):
            if ("BLANK" not in transferState["yourHand"]):
                psg.popup("Your Hand is full! You may need to send the card to Deletion instead!")
            elif (len(transferState["yourDeck"]) == 0):
                psg.popup("Your deck is empty! You (probably) lose the game!")
            else:
                transferState["yourHand"] = [transferState["yourDeck"][0]] + transferState["yourHand"][0:-1]
                transferState["yourDeck"] = transferState["yourDeck"][1:]
                rev = transferState["yourHandRevealed"][0:-1].copy()
                transferState["yourHandRevealed"] = [False] + rev
        elif (event == "shuffleDeck"):
            random.shuffle(transferState["yourDeck"])
        elif (event == "countButton"):
            typeList = [[0, 1, 2, 3, 4], [1], [2, 3], [4]]
            ourTypes = typeList[(["Cards", "Followers", "Amulets", "Spells"]).index(values["countType"])]
            countZone = transferState[values["countWhoseZone"].lower() + values["countLoc"]]
            try:
                comp = int(values["countCNum"])
            except:
                psg.popup("You can only compare against numbers!")
                continue
            if (values["countCompare"] == "Greater Than"):
                compList = list(range(comp + 1, 1000000))
            elif (values["countCompare"] == "Less Than"):
                compList = list(range(0, comp))
            else:
                compList = [comp]
            results = []
            for name in countZone:
                for card in table:
                    if ((card["card_name"] == name) and (card["char_type"] in ourTypes) and (card["cost"] in compList)):
                        results.append(name)
                        break
            psg.popup(str(len(results)))
        elif (event == "randomButton"):
            typeList = [[0, 1, 2, 3, 4], [1], [2, 3], [4]]
            ourTypes = typeList[(["Card", "Follower", "Amulet", "Spell"]).index(values["randomType"])]
            randomZone = transferState[values["randomWhoseZone"].lower() + values["randomLoc"]]
            try:
                comp = int(values["randomCNum"])
            except:
                psg.popup("You can only compare against numbers!")
                continue
            if (values["randomCompare"] == "Greater Than"):
                compList = list(range(comp + 1, 1000000))
            elif (values["randomCompare"] == "Less Than"):
                compList = list(range(0, comp))
            else:
                compList = [comp]
            results = []
            for name in randomZone:
                for card in table:
                    if ((card["card_name"] == name) and (card["char_type"] in ourTypes) and (card["cost"] in compList)):
                        results.append(name)
                        break
            if (len(results) == 0):
                results = ["NONE"]
            psg.popup(random.choice(results))          
        else:
            static = 1
        if (static == 0):
            updateButtons(window, transferState, keyNames)
        
        try:
            event2, values2 = window2.read()
            if (event2 != None):
                longName = "results/" + window2[event2].get_text().replace(" ", "_").replace("//", "~")
                if (os.path.exists(longName + "_base.png") == True):
                    window["yourCardImage"].update(filename = longName + "_base.png")
                    window.refresh()
        except:
            pass

    window.close()
    try:
        window2.close()
    except:
        pass
    connectR.close()
    sockR.close()
    sockS.close()
