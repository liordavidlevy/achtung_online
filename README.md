# Achtung Online


An online python game for 2-3 players, based on the popular Borland C++ game "Achtung, die Kurve!".

![alt text](https://github.com/liorldy/achtung_online/blob/master/res/gif1.gif)

## Getting Started

To play the game you need to use the the d/Right arrow key to turn clockwise and the 'a'/'Left Arrow' key to turn anti-clockwise. You Play as a yellow square which leaves a trail in a unique color on the screen as you move and leave a gap every couple of seconds. If you run into the yellow boarder or into the trail of anither player or yourselfyou die (unless you manage to fit through the latter gap). When one played dies the survivig ones earn on point and when a second player dies the last survivor  earns two points. The goal of the each match in the game is to stay alive as long as you can in order to get overall the most points and eventually get enough to win.

### Prerequisites

Python 2 for running the source code

### Installing

I've icluded a public host-server script and exe file in order to easily run a new room server which aloow to play several maches simultaneously.

There are several ways to run the game:

1. Download Host-Server.exe and Achtung.exe and Run the first executable. This will set up a server to play the game and show the pc's IP address. Then run Achtung.exe, and enter the corresponding IP address. When there are atleast two players in a given room a ney game will start.

2. download the sorce code and run packages.py. The following script will install the necessary modules that are required to run the game. Afterwads, run host_server.py. This will set up a multi-room server in order to play the game and display the pc's IP address. Then run client.py and enter the address and when there are atleast two players in a given room a ney game will start.

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
