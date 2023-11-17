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
import sqlite3
import json

from gameInstance import GameInstance
import utility

class PongServer:
    def __init__(self, ip="localhost", port=1234):
        # ============================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: initializes pongServer
        # Pre: valid ip/port
        # Post: creates a new thread to listen for connections
        # ============================================
        self.instances = {}
        thread = threading.Thread(target=self.listen, args=(ip, port))
        thread.start()

    def add_user_to_database(self, client_socket: socket.socket, username: str, password: str):
        # ============================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: registers a user or checks their password if their username already exists
        # Pre: valid client_socket, username, password (not empty)
        # Post: updates the database or sends a signal indicating a failure
        # ============================================
        # create connection to users.db, where user data is stored
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # create the table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                num_wins INTEGER DEFAULT 0);
            ''');
        
        # attempt to validate password or add user
        try:
            # Check if the username already exists
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            record = cursor.fetchone()

            if record:
                # Username exists, check password
                stored_password = record[0]
                if stored_password != password:
                    # Password does not match
                    utility.send_message(client_socket, {"request": "bad_password"})
                    print(f"Incorrect password for {username} entered.")
                    return False
                else:
                    utility.send_message(client_socket, {"request": "login_success"})
                    return True
            else:
                # Username does not exist, add new user
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                print(f"User {username} added to the database.")
                utility.send_message(client_socket, {"request": "login_success"})
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}", file=sys.stderr)
            return False
        finally:
            conn.close()

    def increment_user_wins(self, username: str):
        # ============================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: increments the number of wins a user has in the DB
        # Pre: valid username that exists in db
        # Post: updates the db
        # ============================================
        conn = sqlite3.connect('users.db')  
        cursor = conn.cursor()

        try:
            # Check if the user exists
            cursor.execute("SELECT num_wins FROM users WHERE username = ?", (username,))
            record = cursor.fetchone()

            if record:
                # User exists, increment num_wins
                num_wins = record[0] + 1
                cursor.execute("UPDATE users SET num_wins = ? WHERE username = ?", (num_wins, username))
                conn.commit()
                print(f"Updated wins for {username}: {num_wins} wins.")
            else:
                # User does not exist
                print(f"User {username} not found in the database.")
        except sqlite3.Error as e:
            print(f"Database error: {e}", file=sys.stderr)
        finally:
            conn.close()

    def listen(self, ip: str, port: int):
        # ============================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: listens for client connections
        # Pre: server is set up and bound to (ip, port)
        # Post: creates new instances and client connections
        # ============================================
        # create a TCP socket instance using IPv4 addressing
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set the socket option to reuse the address. Helps prevent errors
        # such as "address already in use" when restarting the server
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to the ip and port provided
        server.bind((ip, port))

        # allow a maximum of 2 connections to be queued waiting in line
        # before the server will decline new connections
        server.listen(2)
        
        # main loop that listens for client connections
        while True:
            client_socket = None
            addr = None
            try:
                # accept client connection
                client_socket, addr = server.accept()
            except Exception as e:
                print(f"Error in server accepting client connection: {e}", file=sys.stderr)
                continue

            # request their credentials
            request_message = {"request": "credentials"}
            # send the credentials request to the client. continue to next iteration
            # if it fails (will print an error message to stderr)
            if not utility.send_message(client_socket, request_message):
                continue
            
            # receive a response about credentials from the client. If this fails,
            # continue to next iteration (an error message will be printed)
            response = utility.receive_message(client_socket) 
            if not response or response.get("request") != "credentials":
                print(f"Invalid response sent to the server for credentials.", file=sys.stderr)
                continue
            
            # derive the username, hashed password, and gameid they provided
            username = response.get("username")
            password = response.get("password")
            gameid = response.get("gameid")
            if not self.add_user_to_database(client_socket, username, password):
                print(f"username provided invalid password.")
                continue

            # fetch game instance from gameid
            instance = self.find_instance(gameid)

            # if there is no game instance, create a new one and add the player 
            if not instance:
                self.create_instance(gameid)
                instance = self.find_instance(gameid)
            
            # if we fail to add the player, that means the game is full, and thus
            # they cannot join. Send an error message, and close their connection,
            # requiring them to reconnect to the game with a different gameid
            if not instance.add_client_socket(client_socket, username):
                error_msg = {"error": "game is full!"}
                utility.send_message(client_socket, error_msg)
                client_socket.close()
            else:
                thread = threading.Thread(target=self.handle_instance, args=(gameid,))
                thread.start()

    # handle client/server communication for an instance given a gameid
    def handle_instance(self, gameid: str):
        # ============================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: opens up a new thread to handle client communications for one game instance
        # Pre: all other setup has been done regarding the server/client/gameinstance. Has 2 players
        # Post: Handles syncing and updating the state, among other things, via the network
        # ============================================
        # fetch the instance from gameid
        instance = self.find_instance(gameid)

        # if it doesn't find the instance, this is a fatal error
        if not instance:
            raise RuntimeError("Invalid instance in handle_instance!")

        if not instance.is_game_started():
            return
        
        play_again_set = set()
        while True:
            # iterate through both clients in the instance, and handle communications
            for i, client in enumerate(instance.client_sockets):

                data = utility.receive_message(client) 
                if not data:
                    continue
                
                # handle the sync request by sending the server's game state back to the client,
                # so that they can do what is needed to resync their game.
                if data.get("request") == "sync":
                    utility.send_message(client, instance.state)
             
                # collect some variables from the client and ensure that it all matches up
                if data.get("request") == "update_state":
                    # collect variables from the update_state request
                    ypos = data.get("ypos")
                    ballx = data.get("ballx")
                    bally = data.get("bally")
                    ballxvel = data.get("ballxvel")
                    ballyvel = data.get("ballyvel")
                    score = data.get("score")
                    sync = data.get("sync")
                    
                    # check to ensure they're all valid
                    for var in [ypos, ballx, bally, ballxvel, ballyvel, score, sync]:
                        if var is None:
                            print(f"Error: invalid data passed to update_state request. ypos={ypos}, ballx={ballx}, bally={bally}, score={score}, sync={sync}", file=sys.stderr)
                   
                    # update the values in instance
                    instance.set_pos(i, ypos)
                    instance.set_ball_pos(ballx, bally)
                    instance.set_ball_vel(ballxvel, ballyvel)
                    instance.set_score(i, score)
                    instance.set_sync(i, sync)
                    if score >= 1:
                        self.increment_user_wins(instance.get_username(i))
                
                if data.get("request") == "play_again":
                    play_again_set.add(i)
                    print(f"play again received.", file=sys.stderr)
                    if 0 in play_again_set and 1 in play_again_set:
                        instance.set_score(0, 0)
                        instance.set_score(1, 0)
                        play_again_set.clear()

    # retrieves a game instance based on the gameid if it
    # exists
    def find_instance(self, gameid: str):
        # ============================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: fetches an instance from a gameid
        # Pre: none
        # Post: none
        # ============================================
        if gameid in self.instances:
            return self.instances[gameid]

        return None

    # creates a new instance given a gameid
    def create_instance(self, gameid: str):
        # ============================================
        # Author: Kevin Cosby, Oskar Flores
        # Purpose: adds a new instance for the given gameid
        # Pre: none
        # Post: none
        # ============================================
        self.instances[gameid] = GameInstance()

if __name__ == "__main__":
    server = PongServer()

