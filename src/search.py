import os
import FreeSimpleGUI as psg
import json

def searchWindow(table):
    rarities = [ "Token", "Bronze", "Silver", "Gold", "Legendary" ]
    classes = [ "Neutral", "Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft", "Shadowcraft", "Bloodcraft", "Havencraft", "Portalcraft" ]
    types = [ "None", "Follower", "Amulet", "AmuletC", "Spell" ]
    pages = [ "Page 1", "Page 2", "Page 3", "Page 4", "Page 5", "Page 6", "Page 7", "Page 8", "Page 9", "Page 10" ]
    subLay = [
        [ psg.Text("Name:"), psg.Input(key = "name", enable_events = True, default_text = "") ],
        [ psg.Text("   Text:"), psg.Input(key = "text", enable_events = True, default_text = "") ],
        [ psg.Text("Rarity:"), psg.DropDown(["Any"] + rarities, key = "rarity", default_value = "Any") ],
        [ psg.Text("Class:"), psg.DropDown(["Any"] + classes, key = "class", default_value = "Any") ],
        [ psg.Text("  Type:"), psg.DropDown(["Any"] + types, key = "type", default_value = "Any") ],
        [ psg.Text("  Trait:"), psg.Input(key = "subtype", enable_events = True, default_text = "") ],
        [ 
            psg.Text(" Min Cost:"), psg.DropDown([str(x) for x in ["Any"] + list(range(11))], key = "minCost", default_value = "Any"),
            psg.Text(" Min Attack:"), psg.DropDown([str(x) for x in ["Any"] + list(range(21))], key = "minAttack", default_value = "Any"),
            psg.Text(" Min Life:"), psg.DropDown([str(x) for x in ["Any"] + list(range(21))], key = "minLife", default_value = "Any")
        ],
        [ 
            psg.Text("Max Cost:"), psg.DropDown([str(x) for x in ["Any"] + list(range(11))], key = "maxCost", default_value = "Any"),
            psg.Text("Max Attack:"), psg.DropDown([str(x) for x in ["Any"] + list(range(21))], key = "maxAttack", default_value = "Any"),
            psg.Text("Max Life:"), psg.DropDown([str(x) for x in ["Any"] + list(range(21))], key = "maxLife", default_value = "Any")
        ],
        [ psg.Text("", size = (29, 1)), psg.DropDown(pages, key = "page", default_value = "Page 1"), psg.Button("Search", key = "execute") ]
    ]
    textList = [""] * 10
    for i in range(10):
        textList[i] = "Card " + str(i)
        subLay = subLay + [[
            psg.Text("Card " + str(i + 1), key = "cardText" + str(i), size = (29, 1)),
            psg.Button("View Card", key = "view" + str(i))
        ]]
    layout = [
        [
            psg.Column(subLay), psg.Column([[psg.Image("blank_card.png", key = "cardImage"), psg.Image("blank_card.png", key = "cardImageEvo")]])
        ]
    ]
    window = psg.Window("", layout, grab_anywhere = True, resizable = True, return_keyboard_events = True, font = "-size 12")

    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
            break
        elif ((event == "execute") or (event in [ "\r", "special 16777220", "special 16777221" ])): # if you press the Search button or Enter
            subset = []
            names = []
            for card in table:
                if ((values["name"].lower() in card["card_name"].lower()) and (values["text"].lower() in card["skill_disc"].lower())):
                    if ((values["rarity"] == "Any") or (card["rarity"] == rarities.index(values["rarity"]))):
                        if ((values["class"] == "Any") or (card["clan"] == classes.index(values["class"]))):
                            if ((values["type"] == "Any") or (card["char_type"] == types.index(values["type"]))):
                                if (values["subtype"].lower() in card["tribe_name"].lower()):
                                    if ((values["minCost"] == "Any") or (card["cost"] >= int(values["minCost"]))):
                                        if ((values["minAttack"] == "Any") or (card["atk"] >= int(values["minAttack"]))):
                                            if ((values["minLife"] == "Any") or (card["life"] >= int(values["minLife"]))):
                                                if ((values["maxCost"] == "Any") or (card["cost"] <= int(values["maxCost"]))):
                                                    if ((values["maxAttack"] == "Any") or (card["atk"] <= int(values["maxAttack"]))):
                                                        if ((values["maxLife"] == "Any") or (card["life"] <= int(values["maxLife"]))):
                                                            if (card["card_name"] not in names):
                                                                subset.append(card)
                                                                names.append(card["card_name"])
            for i in range(10):
                page = int(values["page"].split(" ")[1]) - 1
                curr = i + (page * 10)
                if (len(subset) > curr):
                    window["cardText" + str(i)].update(subset[curr]["card_name"])
                    textList[i] = subset[curr]["card_name"]
                else:
                    window["cardText" + str(i)].update("Card " + str(i + 1))
                    textList[i] = "Card " + str(i)
                                 
        for i in range(10):
            if (event == "view" + str(i)):
                if (textList[i] != "Card " + str(i)):
                    if (os.path.exists("./results/" + textList[i].replace(" ", "_") + "_evolved.png")):
                        window["cardImage"].update(filename = "./results/" + textList[i].replace(" ", "_") + "_base.png")
                        window["cardImageEvo"].update(filename = "./results/" + textList[i].replace(" ", "_") + "_evolved.png")
                    else:
                        window["cardImage"].update(filename = "./results/" + textList[i].replace(" ", "_") + "_base.png")  
                        window["cardImageEvo"].update(filename = "blank_card.png")                        
            
    # Finish up by removing from the screen
    window.close()
