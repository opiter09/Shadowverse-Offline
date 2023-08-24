import os
import sys
import string
from PIL import Image
import math
import json
import textwrap

def createImages(table):
    try:
        os.mkdir("results")
    except OSError as error:
        pass

    corr = ([""] * 32) + [ " ", "!", '"', "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/" ]
    corr = corr + [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":", ";", "<", "=", ">", "?", "@" ]
    corr = corr + list(string.ascii_uppercase) + [ "[", "\\", "]", "^", "_", "`" ]
    corr = corr + list(string.ascii_lowercase) + [ "{", "|", "}", "~" ]

    rarities = [ "Token", "Bronze", "Silver", "Gold", "Legendary" ]
    classes = [ "Neutral", "Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft", "Shadowcraft", "Bloodcraft", "Havencraft", "Portalcraft", "Abysscraft" ]
    types = [ "None", "Follower", "Amulet", "Amulet", "Spell" ]
    for card in table:
        if (os.path.exists("results/" + card["card_name"].replace(" ", "_").replace("//", "~") + "_base.png") == True):
            continue

        if (card["tribe_name"] == "-"):
            card["tribe_name"] = ""
        if (card["evo_skill_disc"] == "(Same as the unevolved form.)"):
            card["evo_skill_disc"] = card["skill_disc"]
        elif (card["evo_skill_disc"].split("<br>")[0] == "(Same as the unevolved form, excluding Fanfare.)"):
            oldList = card["evo_skill_disc"].split("<br>")
            card["evo_skill_disc"] = ""
            splits = card["skill_disc"].split("<br>")
            for i in range(len(splits)):
                if (splits[i].startswith("Fanfare:") == False):
                    card["evo_skill_disc"] = card["evo_skill_disc"] + splits[i]
                    if (i != (len(splits) - 1)):
                        card["evo_skill_disc"] = card["evo_skill_disc"] + "<br>"
            if (len(oldList) > 1):
                for i in range(1, len(oldList)):
                    card["evo_skill_disc"] = card["evo_skill_disc"] + oldList[i]
                    if (i != (len(oldList) - 1)):
                        card["evo_skill_disc"] = card["evo_skill_disc"] + "<br>"
                    
                

        text = [ "", "", card["card_name"], "BASE   " + "   (" + str(card["cost"]) + ")", "[" + rarities[card["rarity"]] + "] " \
        + types[card["char_type"]], classes[card["clan"]] + " " + card["tribe_name"], "", "" ] \
        + card["skill_disc"].replace("<br><br>", "<br>").replace("<br>", "\n").replace("[b]", "").replace("[\b]", "").split("\n") \
        + [ "", "" ] + card["description"].replace("<br>", "\n").split("\n")
        if (card["char_type"] == 1):
            text = text + [ "", "", "ATK: " + str(card["atk"]) + "   DEF: " + str(card["life"]) ]
        
        temp = ""
        for line in text:
            if (len(line) != 0):
                new = textwrap.wrap(line, width = 24)
                for item in new:
                    if ((len(item) % 24) != 0):
                        temp = temp + "  " + item + (" " * (24 - (len(item) % 24))) + "  "
                    else:
                        temp = temp + "  " + item + "  "
            else:
                temp = temp + line + (" " * 28)
        im = Image.new("RGBA", size = (336, 468), color = (255, 255, 255)) # 28 x 39
        
        if (len(temp) > (28 * 37)):
            text = [ "", "", card["card_name"], "BASE   " + "   (" + str(card["cost"]) + ")", "[" + rarities[card["rarity"]] + "] " \
            + types[card["char_type"]], classes[card["clan"]] + " " + card["tribe_name"], "", "" ] \
            + card["skill_disc"].replace("<br><br>", "<br>").replace("<br>", "\n").replace("[b]", "").replace("[\b]", "").split("\n")
            if (card["char_type"] == 1):
                text = text + [ "", "", "ATK: " + str(card["atk"]) + "   DEF: " + str(card["life"]) ]         
            temp = ""
            for line in text:
                if (len(line) != 0):
                    new = textwrap.wrap(line, width = 24)
                    for item in new:
                        if ((len(item) % 24) != 0):
                            temp = temp + "  " + item + (" " * (24 - (len(item) % 24))) + "  "
                        else:
                            temp = temp + "  " + item + "  "
                else:
                    temp = temp + line + (" " * 28)
        if (len(temp) > (28 * 37)):
            print(card["card_name"])
        im = Image.new("RGBA", size = (336, 468), color = (255, 255, 255)) # 28 x 39
        count = -1
        for ch in temp:
            count = count + 1
            if (count >= (28 * 37)):
                break
            else:
                sub = Image.open("./pieces/" + str(corr.index(ch) + 1) + ".png")
                im.paste(sub, ((count % 28) * 12, math.floor(count / 28) * 12))
                sub.close()
        im.save("results/" + card["card_name"].replace(" ", "_").replace("//", "~") + "_base.png")

        if (card["char_type"] != 1):
            continue

        text = [ "", "", card["card_name"], "EVOLVED" + "   (" + str(card["cost"]) + ")", "[" + rarities[card["rarity"]] + "] " \
        + types[card["char_type"]], classes[card["clan"]] + " " + card["tribe_name"], "", "" ] \
        + card["evo_skill_disc"].replace("<br><br>", "<br>").replace("<br>", "\n").replace("[b]", "").replace("[\b]", "").split("\n") \
        + [ "", "" ] + card["evo_description"].replace("<br>", "\n").split("\n")
        if (card["char_type"] == 1):
            text = text + [ "", "", "ATK: " + str(card["evo_atk"]) + "   DEF: " + str(card["evo_life"]) ]
        
        temp = ""
        for line in text:
            if (len(line) != 0):
                new = textwrap.wrap(line, width = 24)
                for item in new:
                    if ((len(item) % 24) != 0):
                        temp = temp + "  " + item + (" " * (24 - (len(item) % 24))) + "  "
                    else:
                        temp = temp + "  " + item + "  "
            else:
                temp = temp + line + (" " * 28)
        im = Image.new("RGBA", size = (336, 468), color = (255, 255, 255)) # 28 x 39
        
        if (len(temp) > (28 * 37)):
            text = [ "", "", card["card_name"], "EVOLVED" + "   (" + str(card["cost"]) + ")", "[" + rarities[card["rarity"]] + "] " \
            + types[card["char_type"]], classes[card["clan"]] + " " + card["tribe_name"], "", "" ] \
            + card["evo_skill_disc"].replace("<br><br>", "<br>").replace("<br>", "\n").replace("[b]", "").replace("[\b]", "").split("\n")
            if (card["char_type"] == 1):
                text = text + [ "", "", "ATK: " + str(card["evo_atk"]) + "   DEF: " + str(card["evo_life"]) ]            
            temp = ""
            for line in text:
                if (len(line) != 0):
                    new = textwrap.wrap(line, width = 24)
                    for item in new:
                        if ((len(item) % 24) != 0):
                            temp = temp + "  " + item + (" " * (24 - (len(item) % 24))) + "  "
                        else:
                            temp = temp + "  " + item + "  "
                else:
                    temp = temp + line + (" " * 28)
        if (len(temp) > (28 * 37)):
            print(card["card_name"] + " EVOLVED")
        count = -1
        for ch in temp:
            count = count + 1
            if (count >= (28 * 37)):
                break
            else:
                sub = Image.open("./pieces/" + str(corr.index(ch) + 1) + ".png")
                im.paste(sub, ((count % 28) * 12, math.floor(count / 28) * 12))
                sub.close()
        im.save("results/" + card["card_name"].replace(" ", "_").replace("//", "~") + "_evolved.png")
        
        # print(card["card_name"] + " finished")