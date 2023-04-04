import os
import sys
import PySimpleGUI as psg
import json
import random

def deckImport(table):
    f = open("deck1.txt", "rt")
    deck1 = f.read().split("\n")
    f.close()
    f = open("deck2.txt", "rt")
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