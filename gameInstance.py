# =================================================================================================
# Contributing Authors:	    Kevin Cosby, Oskar Flores 
# Email Addresses:          knco259@uky.edu, oskar.flores@uky.edu
# Date:                     2023 November 15
# Purpose:                  handles the client side of the game
# Misc:                     Released under GNU GPL v3.0
# =================================================================================================

import sys
import socket
import threading
import json

import utility

class GameInstance:
    def __init__(self):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: constructor for gameinstance
        # Pre: none
        # Post: sets up GameInstance vars
        # ====================================================
        self.state = {
            "p1_ypos": 0,
            "p2_ypos": 0,
            "ballx": 0,
            "bally": 0,
            "ballxvel": 0,
            "ballyvel": 0,
            "p1_score": 0,
            "p2_score": 0,
            "game_started": False,
            "p1_sync": 0,
            "p2_sync": 0,
        }

        self.start_game_request = {
            "request": "start_game",
            "x_res": 640,
            "y_res": 480,
            "paddle": "Unknown",
        }

        self.client_sockets = []
        self.usernames = []

    def add_client_socket(self, client_socket: socket.socket, username: str) -> bool:
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: adds a socket to this game instance
        # Pre: socket/username must be valid
        # Post: maintains lists containing sockets/usernames, sends a signal when 2 players have joined
        # ====================================================
        if len(self.client_sockets) >= 2:
            return False

        self.client_sockets.append(client_socket)
        self.usernames.append(username)
        if len(self.client_sockets) == 2:
            self.state["game_started"] = True
            for i, client in enumerate(self.client_sockets):
                self.start_game_request["paddle"] = f"player{i+1}"
                utility.send_message(client, self.start_game_request)

        return True
   
    def get_username(self, i: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: returns the username for a given client
        # Pre: i is in [0, 1]
        # Post: none
        # ====================================================
        return self.usernames[i]

    def is_game_started(self) -> bool:
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: checks if game_started is true
        # Pre: none
        # Post: none
        # ====================================================
        return self.state["game_started"]

    def set_pos(self, index: int, y: int) -> bool:
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores 
        # Purpose: sets position of a client's paddle 
        # Pre: index is in [0, 1]
        # Post: state is updated
        # ====================================================

        if index not in [0, 1]:
            return False

        if index == 0:
            self.set_p1_pos(y)
        else:
            self.set_p2_pos(y)

        return True

    def set_score(self, index: int, score: int) -> bool:
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets player's score
        # Pre: none
        # Post: sets score for player{index} in state
        # ====================================================
        if index not in [0, 1]:
            return False

        if index == 0:
            self.set_p1_score(score)
        else:
            self.set_p2_score(score)

        return True

    def set_sync(self, index: int, sync: int) -> bool:
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets sync for a player
        # Pre: none
        # Post: sets sync in state for given player
        # ====================================================
        if index not in [0, 1]:
            return False

        if index == 0:
            self.set_p1_sync(sync)
        else:
            self.set_p2_sync(sync)

        return True


    def set_p1_pos(self, y: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets p1 pos
        # Pre: none
        # Post: sets p1_ypos in state
        # ====================================================
        self.state["p1_ypos"] = y

    def set_p2_pos(self, y: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets p2 pos
        # Pre: none
        # Post: sets p2_ypos in state
        # ====================================================
        self.state["p2_ypos"] = y

    def set_players_pos(self, p1_y: int, p2_y: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets both players' y pos
        # Pre: none
        # Post: sets p1/p2 pos in state
        # ====================================================
        self.set_p1_pos(p1_y)
        self.set_p2_pos(p2_y)

    def set_p1_score(self, score: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets p1 score
        # Pre: none
        # Post: sets p1_score in state
        # ====================================================
        self.state["p1_score"] = score
    
    def set_p2_score(self, score: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets p2 score
        # Pre: none
        # Post: sets p2_score in state
        # ====================================================
        self.state["p2_score"] = score

    def set_players_score(self, p1_score: int, p2_score: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets p1 and p2 scores
        # Pre: none
        # Post: sets both players' scores
        # ====================================================
        self.set_p1_score(p1_score)
        self.set_p2_score(p2_score)
   
    def set_ball_pos(self, x: int, y: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets ball position (x, y)
        # Pre: none
        # Post: ballx and bally set to (x, y) in state
        # ====================================================
        self.state["ballx"] = x
        self.state["bally"] = y

    def start_game(self):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: sets game_started to true
        # Pre: none
        # Post: game_started set to true in state 
        # ====================================================
        self.state["game_started"] = True

    def set_p1_sync(self, sync: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: setter for sync (p1)
        # Pre: none
        # Post: sets p1_sync in state
        # ====================================================
        self.state["p1_sync"] = sync

    def set_p2_sync(self, sync: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose:  setter for sync (p2)
        # Pre: none
        # Post: sets p2_sync in state
        # ====================================================
        self.state["p2_sync"] = sync

    def set_ball_vel(self, xv: int, yv: int):
        # ====================================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: setter for ball velocity
        # Pre: none
        # Post: sets ballxvel and ballyvel in state
        # ====================================================
        self.state["ballxvel"] = xv
        self.state["ballyvel"] = yv
