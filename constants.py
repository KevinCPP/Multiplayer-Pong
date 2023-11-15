import socket
import json

encoding_scheme = 'utf-8'
data_size = 1024

def send_message(socket, message):
    msg = json.dumps(message)
    socket.sendall(msg.encode(encoding_scheme))

def receive_message(socket):
    response = socket.recv(data_size).decode(encoding_scheme)
    return json.loads(response)

