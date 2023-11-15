# =================================================================================================
# Contributing Authors:	    Kevin Cosby, Oskar Flores 
# Email Addresses:          knco259@uky.edu, oskar.flores@uky.edu
# Date:                     2023 November 15
# Purpose:                  handles the client side of the game
# Misc:                     Released under GNU GPL v3.0
# =================================================================================================

import sys
import socket
import json

encoding_scheme = 'utf-8'
data_size = 256
length_prefix_size = 4

def send_message(sock, message):
    try:
        msg = json.dumps(message).encode(encoding_scheme)
        length_prefix = len(msg).to_bytes(length_prefix_size, byteorder='big')
#        print(f"sending: {length_prefix + msg}")
        sock.sendall(length_prefix + msg)
        return True
    except (socket.error, json.JSONDecodeError) as e:
        print(f"Failed to send message to socket.\nMessage: {message}\nException: {e}", file=sys.stderr)
        return False

def receive_message(sock):
    try:
        length_bytes = sock.recv(length_prefix_size)
        if not length_bytes:
            return None

        length = int.from_bytes(length_bytes, byteorder='big')
        
        response = sock.recv(length)
#        print(f"response: {response}")
        if not response:
            return None  # No data received
        
        response = response.decode(encoding_scheme)
        
        return json.loads(response)
    except (socket.error, json.JSONDecodeError) as e:
        print(f"Failed to receive message from socket.\nException: {e}", file=sys.stderr)
        return None

