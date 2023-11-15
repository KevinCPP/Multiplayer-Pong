import sys
import socket
import threading
import json

from gameInstance import GameInstance
import utility

class PongServer:
    def __init__(self, ip="localhost", port=1234):
        self.instances = {}
        thread = threading.Thread(target=self.listen, args=(ip, port))
        thread.start()

    def listen(self, ip, port):
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
            
            # fetch game instance from gameid
            instance = self.find_instance(gameid)

            # if there is no game instance, create a new one and add the player 
            if not instance:
                self.create_instance(gameid)
                instance = self.find_instance(gameid)
            
            # if we fail to add the player, that means the game is full, and thus
            # they cannot join. Send an error message, and close their connection,
            # requiring them to reconnect to the game with a different gameid
            if not instance.add_client_socket(client_socket):
                error_msg = {"error": "game is full!"}
                utility.send_message(client_socket, error_msg)
                client_socket.close()
            else:
                thread = threading.Thread(target=self.handle_instance, args=(gameid,))
                thread.start()
    
    # handle client/server communication for an instance given a gameid
    def handle_instance(self, gameid):
        # fetch the instance from gameid
        instance = self.find_instance(gameid)

        # if it doesn't find the instance, this is a fatal error
        if not instance:
            raise RuntimeError("Invalid instance in handle_instance!")

        if not instance.is_game_started():
            return
        
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


    # retrieves a game instance based on the gameid if it
    # exists
    def find_instance(self, gameid):
        if gameid in self.instances:
            return self.instances[gameid]

        return None

    # creates a new instance given a gameid
    def create_instance(self, gameid):
        self.instances[gameid] = GameInstance()

if __name__ == "__main__":
    server = PongServer()

