import os
import sys
import PySimpleGUI as psg
import json
import random

def deckImport(table):
    file1 = psg.popup_get_file("Select the first deck file:", file_types = [("Text Files", "*.txt")])
    if (os.path.exists(file1) == False):
        file1 = "deck1.txt"
    file2 = psg.popup_get_file("Select the second deck file:", file_types = [("Text Files", "*.txt")])
    if (os.path.exists(file2) == False):
        file2 = "deck2.txt"

    f = open(file1, "rt")
    deck1 = f.read().split("\n")
    f.close()
    f = open(file2, "rt")
    deck2 = f.read().split("\n")
    f.close()
    
    if ((len(deck1) != 40) or (len(deck2) != 40)):
        print("Invalid deck! Improper deck size detected!")
        return(None, None)

    bad = 0
    prev = "Neutral"
    for i in range(len(deck1)):
        if (bad > 0):
            break
        for card in table:
            if (card["card_name"] != None):
                if (card["card_name"].lower().replace(" ", "") == deck1[i].lower().replace(" ", "")):
                    if ((prev != "Neutral") and (card["clan"] != "Neutral") and (card["clan"] != prev)):
                        bad = 1
                    else:
                        prev = card["clan"]
                        deck1[i] = card
                    break
        if (type(deck1[i]) == str):
            print(deck1[i])
            bad = 2
    if (bad == 1):
        print("Invalid deck! Cards of multiple classes detected!")
        return(None, None)
    elif (bad == 2):
        print("Invalid deck! Nonexistant cards detected!")
        return(None, None)        
        
    bad = 0
    prev = "Neutral"
    for i in range(len(deck2)):
        if (bad > 0):
            break
        for card in table:
            if (card["card_name"] != None):
                if (card["card_name"].lower().replace(" ", "") == deck2[i].lower().replace(" ", "")):
                    if ((prev != "Neutral") and (card["clan"] != "Neutral") and (card["clan"] != prev)):
                        bad = 1
                    else:
                        prev = card["clan"]
                        deck2[i] = card
                    break
        if (type(deck2[i]) == str):
            print(deck2[i])
            bad = 2
    if (bad == 1):
        print("Invalid deck! Cards of multiple classes detected!")
        return(None, None)
    elif (bad == 2):
        print("Invalid deck! Nonexistant cards detected!")
        return(None, None)
    
    return(deck1, deck2)

def playBall(table):
    deck1, deck2 = deckImport(table)
    if (deck1 == None):
        return
    random.shuffle(deck1)
    random.shuffle(deck2)