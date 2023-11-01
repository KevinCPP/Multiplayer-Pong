# =================================================================================================
# Contributing Authors:	    Oskar Flores, Kevin Cosby 
# Email Addresses:          knco259@uky.edu, oskar.flores@uky.edu 
# Date:                     2023-11-01
# Purpose:                  Multiplayer Pong Project (server functionality)
# Misc:                     Released under GNU GPL v3.0
# =================================================================================================

import socket
import threading

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games
