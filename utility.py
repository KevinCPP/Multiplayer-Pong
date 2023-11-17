# =================================================================================================
# Contributing Authors:	    Kevin Cosby, Oskar Flores 
# Email Addresses:          knco259@uky.edu, oskar.flores@uky.edu
# Date:                     2023 November 15
# Purpose:                  handles the sending/receiving of messages
# Misc:                     Released under GNU GPL v3.0
# =================================================================================================

import sys
import socket
import json

# constants to be used throughout this
encoding_scheme = 'utf-8'
data_size = 256
length_prefix_size = 4

def send_message(sock: socket.socket, message: dict):

    # ============================================================
    # Author: Kevin Cosby, Oskar Flores
    # Purpose: sends messages to the socket
    # pre: valid socket and message
    # post: message is encoded as json and sent to the socket
    # ============================================================
    try:
        # encode the message for transmission
        msg = json.dumps(message).encode(encoding_scheme)
        # create a length prefix based off of the length of the encoded message
        length_prefix = len(msg).to_bytes(length_prefix_size, byteorder='big')
        # send the message with the length_prefix preappended
        sock.sendall(length_prefix + msg)
        # return true on success
        return True
    except (socket.error, json.JSONDecodeError) as e:
        # print an error message if an exception was encountered, return false for failure
        print(f"Failed to send message to socket.\nMessage: {message}\nException: {e}", file=sys.stderr)
        return False

def receive_message(sock: socket.socket):
    # ============================================================
    # Author: Kevin Cosby, Oskar Flores
    # Purpose: Receives a message from the socket
    # pre: valid socket
    # post: none
    # ============================================================

    try:
        # extract length prefix
        length_bytes = sock.recv(length_prefix_size)
        if not length_bytes:
            return None
        
        # convert length prefix into an integer
        length = int.from_bytes(length_bytes, byteorder='big')
        
        # read length bytes from the socket
        response = sock.recv(length)
        if not response:
            return None  # No data received
        
        # decode the received message
        response = response.decode(encoding_scheme)
        
        # return the json data
        return json.loads(response)
    except (socket.error, json.JSONDecodeError) as e:
        # print an error message if we got an exception
        print(f"Failed to receive message from socket.\nException: {e}", file=sys.stderr)
        return None

