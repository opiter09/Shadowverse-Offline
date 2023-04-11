# Shadowverse-Offline
This is a stupid little project that lets you search and sort of play with Shadowverse cards offline. The cards are just images of the text, without artwork or voice acting or anything, so
it's nothing like the actual game. And the WIP game engine will have very little actual rules enforcement, similar to the website https://www.untap.in.
Oh and I sure as hell am not learning actual Internet code, so this will be made using cobbled-together LAN programming. But at least the search doesn't require you to go through
all the app's menus, and you will be able to play with any card that exists in the game as of March 2023 (or beyond if you are willing to supply your own json).

THE HOST NEEDS TO START (AND GO THROUGH ALL THREE MENUS) BEFORE THE CLIENT!!!

This program requires both you and your friend's IP Address. To get that, open the Command Prompt (in Windows) and type in "ipconfig." The value you see will be listed as the
"IPv4 address." To save time, you can write both addresses in the provied IPv4.txt file, with your address on one line, and your friend's on the next. Then, when prompted for
your addresses, just hit "Ok" without typing anything in.

To download these files, please press the green "Code" button, then choose "Download ZIP."

# Credits
- Thanks to PySimpleGUI, for making it very easy for me to make GUIs for this stuff
- Thanks to zxt for making https://github.com/zxt/shadowverse-portal, which is how I original got the card data json
- Thanks to the tcod team, for creating the font used in the cards. This font is in the public domain, and is originally from here:
https://github.com/libtcod/python-tcod/tree/11.13.5/fonts/libtcod
