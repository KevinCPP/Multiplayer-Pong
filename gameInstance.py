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

    def add_client_socket(self, client_socket) -> bool:
        if len(self.client_sockets) >= 2:
            return False

        self.client_sockets.append(client_socket)
        if len(self.client_sockets) == 2:
            self.state["game_started"] = True
            for i, client in enumerate(self.client_sockets):
                self.start_game_request["paddle"] = f"player{i+1}"
                utility.send_message(client, self.start_game_request)

        return True
    
    def is_game_started(self) -> bool:
        return self.state["game_started"]

    def get_encoded_state(self) -> bytes:
        return json.dumps(self.state).encode(utility.encoding_scheme)

    def set_pos(self, index: int, y: int) -> bool:
        if index not in [0, 1]:
            return False

        if index == 0:
            self.set_p1_pos(y)
        else:
            self.set_p2_pos(y)

        return True

    def set_score(self, index: int, score: int) -> bool:
        if index not in [0, 1]:
            return False

        if index == 0:
            self.set_p1_score(score)
        else:
            self.set_p2_score(score)

        return True

    def set_sync(self, index: int, sync: int) -> bool:
        if index not in [0, 1]:
            return False

        if index == 0:
            self.set_p1_sync(sync)
        else:
            self.set_p2_sync(sync)

        return True


    def set_p1_pos(self, y: int):
        self.state["p1_ypos"] = y

    def set_p2_pos(self, y: int):
        self.state["p2_ypos"] = y

    def set_players_pos(self, p1_y: int, p2_y: int):
        self.set_p1_pos(p1_y)
        self.set_p2_pos(p2_y)

    def set_p1_score(self, score: int):
        self.state["p1_score"] = score
    
    def set_p2_score(self, score: int):
        self.state["p2_score"] = score

    def set_players_score(self, p1_score: int, p2_score: int):
        self.set_p1_score(p1_score)
        self.set_p2_score(p2_score)
   
    def set_ball_pos(self, x: int, y: int):
        self.state["ballx"] = x
        self.state["bally"] = y

    def start_game(self):
        self.state["game_started"] = True

    def set_p1_sync(self, sync: int):
        self.state["p1_sync"] = sync

    def set_p2_sync(self, sync: int):
        self.state["p2_sync"] = sync

    def set_ball_vel(self, xv: int, yv: int):
        self.state["ballxvel"] = xv
        self.state["ballyvel"] = yv
