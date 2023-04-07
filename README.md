# Shadowverse-Offline
This is a stupid little project that lets you search and sort of play with Shadowverse cards offline. The cards are just images of the text, without artwork or voice acting or anything, so
it's nothing like the actual game. And the WIP game engine will have very little actual rules enforcement, similar to the website https://www.untap.in.
Oh and I sure as hell am not learning actual Internet code, so this will be made using cobbled-together LAN programming. But at least the search doesn't require you to go through
all the app's menus, and you will be able to play with any card that exists in the game as of March 2023 (or beyond if you are willing to supply your own json).

THE HOST NEEDS TO START (AND GO THROUGH ALL THREE MENUS) BEFORE THE CLIENT!!!

# Note
This program is designed to run on Windows. Normally, the whole Python thing would make it quite portable, but there are a few things Stack Overflow tells me work a little differently
on other platforms. Here is a list of differences I have found:
- os.startfile(filename) in search.py needs to be replaced with subprocess.call(("xdg-open", filepath))
- subprocess.Popen(["ipconfig"]) in main.py needs to be replaced with subprocess.Popen(["ifconfig"]) (or some equivalent function that runs "ifconfig," if needed)

# Credits
- Thanks to PySimpleGUI, for making it very easy for me to make GUIs for this stuff
- Thanks to zxt for making https://github.com/zxt/shadowverse-portal, which is how I original got the card data json
- Thanks to the tcod team, for creating the font used in the cards. This font is in the public domain, and is originally from here:
https://github.com/libtcod/python-tcod/tree/11.13.5/fonts/libtcod
