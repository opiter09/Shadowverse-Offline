# Shadowverse-Offline
This is a stupid little project that lets you search and sort of play with Shadowverse cards offline. The cards are just images of the text, without artwork or voice acting or anything,
so it's nothing like the actual game. This game "engine" has very little actual rules enforcement, similar to the website https://www.untap.in.
Oh and I sure as hell am not learning actual Internet code, so this has been made using cobbled-together LAN programming. But at least the search doesn't require you to go through
all the app's menus, and you are able to play with any card that exists in the game as of March 2023 (or beyond if you are willing to supply your own json).

# Notes
- To download these files, please press the green "Code" button, then choose "Download ZIP."
- When the application first runs, it will appear to do nothing. Notice, however, the generation of a folder named "results." If you go in that folder, you will see images constantly
  being added. Eventually, all the images (of card text) will be finished, and then the program will start for real. This process only occurs once, so do not worry.
- THE HOST NEEDS TO START (AND GO THROUGH ALL THREE MENUS) BEFORE THE CLIENT!!!
- This program requires both you and your friend's IP Address. To get that, open the Command Prompt (in Windows), type in "ipconfig", and then press Enter. The value you seek will
  be listed as the "IPv4 address." To save time, you can write both addresses in the provied IPv4.txt file, with your address on one line, and your friend's on the next. Then, when
  prompted for your addresses, just hit "Ok" without typing anything in.
- Similarly, if you put your deck inside the provided Deck.txt file (in the demonstrated format of one card per line), you can just press "Ok" at the deck file selection window, and
  Deck.txt will be automatically used.

# Credits
- Thanks to PySimpleGUI, for making it very easy for me to make GUIs for this stuff
- Thanks to zxt for making https://github.com/zxt/shadowverse-portal, which is how I original got the card data json
- Thanks to the tcod team, for creating the font used in the cards. This font is in the public domain, and is originally from here:
  https://github.com/libtcod/python-tcod/blob/11.13.5/fonts/libtcod/terminal12x12_gs_ro.png
