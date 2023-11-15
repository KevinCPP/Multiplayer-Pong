import socket
import threading
import json

def handle_client(client_socket, player_id, opponent_id, clients):
    global game_state

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            client_request = json.loads(data.decode('utf-8'))

            if client_request["request"] == "update_paddle":
                # Update the paddle position for this player
                game_state[player_id]['y_pos'] = client_request['y_pos']

            elif client_request["request"] == "get_opponent_paddle":
                # Send the opponent's paddle position to this player
                response = {'opponent_y': game_state[opponent_id]['y_pos']}
                client_socket.sendall(json.dumps(response).encode('utf-8'))

            elif client_request["request"] == "get_parameters":
                # Send game parameters to the player
                response = {
                    'x_res': 400,  # Example resolution, adjust as needed
                    'y_res': 480,
                    'paddle_position': player_id
                }
                client_socket.sendall(json.dumps(response).encode('utf-8'))

        # Handle readiness message
            if client_request['request'] == 'ready':
                client_ready[player_id] = True
                # Check if both clients are ready
                if all(client_ready.values()):
                    # Notify clients to start the game
                    for c in clients:
                        response = {'game_start': True}
                        c.sendall(json.dumps(response).encode('utf-8'))


            if client_request['request'] == 'score':
                # Update score for the player
                game_state[player_id]['score'] += 1
                # Send score update to both clients
                score_update = {'player1_score': game_state['player1']['score'], 'player2_score': game_state['player2']['score']}
                for c in clients:
                    c.sendall(json.dumps(score_update).encode('utf-8'))


        except Exception as e:
            print(f"Error with client {player_id}: {e}")
            break

    # Regularly send game state updates
    while True:
        try:
            # Send current game state to client
            client_socket.sendall(json.dumps(game_state).encode('utf-8'))
            time.sleep(0.1)  # Adjust this to control update frequency
        except Exception as e:
            print(f'Error sending game state to {player_id}: {e}')
            break

    client_socket.close()
    print(f"Client {player_id} disconnected")

client_ready = {'player1': False, 'player2': False}

def start_server():
    global game_state
    game_state = {'player1': {'y_pos': 0, 'score': 0}, 'player2': {'y_pos': 0, 'score': 0}, 'ball': {'x': 320, 'y': 240}}

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 12321))
    server.listen(2)
    print("Server listening for connections...")

    clients = []

    while len(clients) < 2:
        client_socket, addr = server.accept()
        player_id = 'player1' if len(clients) == 0 else 'player2'
        opponent_id = 'player2' if player_id == 'player1' else 'player1'
        print(f"Connection from {addr} as {player_id}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket, player_id, opponent_id, clients))
        client_thread.start()
        clients.append(client_socket)

    print("Both players connected. Game can start.")

if __name__ == "__main__":
    start_server()


