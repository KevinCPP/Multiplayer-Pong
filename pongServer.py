# =================================================================================================
# Contributing Authors:	    Kevin Cosby, Oskar Flores 
# Email Addresses:          knco259@uky.edu, oskar.flores@uky.edu
# Date:                     2023 November 1
# Purpose:                  handles the client side of the game
# Misc:                     Released under GNU GPL v3.0
# =================================================================================================

import socket
import threading
import json

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

# Author:        Kevin Cosby, Oskar Flores
    #
    # Purpose:       Receives the paddle y-position from the client and handles any errors or       exceptions gracefully
    # Pre:           expects an integer value, otherwise an exception will be raised.
    #                this method can hide the window and kill the app once the game is over
    #
    # Post:          This method will update the client's paddle position
    #
    # Arguments:
    #                client_socket            A string holding the IP address of the server

import socket
import threading
import json


# Store the state of the game.
game_state = {
    'player1': {'y_pos': 0},
    'player2': {'y_pos': 0}
}

connected_clients = 0

def handle_client_info(client_socket):
    global game_state
    global connected_clients
    
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            # Decode and parse the request from the client
            decoded_data = data.decode('utf-8')
            client_request = json.loads(decoded_data)
            
            if client_request["request"] == "update_paddle":
                game_state['player1']['y_pos'] = int (client_request['y_pos'])

            elif client_request["request"] == "get_opponent_paddle":
                response = {
                    'opponent_y': game_state['player2']['y_pos']
                }
                client_socket.sendall(json.dumps(response).encode('utf-8'))

            elif client_request["request"] == "get_parameters":
                response = {
                    'x_res': 400,
                    'y_res': 300,
                    'paddle_position': 'left'
                }
                client_socket.sendall(json.dumps(response).encode('utf-8'))

        # After processing other requests, check for game start condition
        if connected_clients == 2:
            start_message = {'request': 'start_game'}
            client_socket.sendall(json.dumps(start_message).encode('utf-8'))

    except Exception as e:
        print(f"Error in handling client: {e}")
    finally:
        client_socket.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 12321))
server.listen(5)

print("Server is listening for connections...")

while True:
    clientSocket, clientAddress = server.accept()
    connected_clients += 1
    print(f"Accepted connection from {clientAddress}")
    
    # Check for game start condition right after accepting a new connection
    if connected_clients == 2:
        start_message = {'request': 'start_game'}
        for client in [clientSocket]:  # Here, you'd broadcast to all connected clients
            client.sendall(json.dumps(start_message).encode('utf-8'))
    
    client_thread = threading.Thread(target=handle_client_info, args=(clientSocket,))
    client_thread.start()

