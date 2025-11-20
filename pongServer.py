# =================================================================================================
# Contributing Authors:	    Nathan Edwards
# Email Addresses:          nathan.edwards281@uky.edu
# Date:                     November 19th, 2025
# Purpose:                  This file will contain all of the server side logic to work with the client
#                           side to make sure the pong game all works correctly with all parts 
#                           flowing together to correctly operate.
# Misc:                     
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

# Shared state for both of the two clients
game_state = {
    "leftpaddle": 215,
    "rightpaddle": 215,
    "ballX": 320,
    "ballY": 240,
    "lScore": 0,
    "rScore": 0,
    "sync": [0,0]   # Sync counters for both the left and right players
}

clients = [None, None]

def handle_client(conn, player_id):
    global game_state
    
    opponent_id = 1 - player_id

    while True:
        try:
            raw = conn.recv(1024)

            if not raw:
                break

            data = json.loads(raw.decode())

            # Update player paddles
            if player_id == 0:
                game_state["leftpaddle"] = data["paddleY"]
            else:
                game_state["rightpaddle"] = data["paddleY"]

            # Update the sync counter
            game_state["sync"][player_id] = data["sync"]

            # Build message with full game state
            msg = {
                "opponentPaddleY": (
                    game_state["rightpaddle"]
                    if player_id == 0
                    else game_state["leftpaddle"]
                ),

                "ballX": game_state["ballX"],
                "ballY": game_state["ballY"],
                "lScore": game_state["lScore"],
                "rScore": game_state["rScore"],
                "syncOpp": game_state["sync"][opponent_id]
            }

            conn.send(json.dumps(msg).encode())

        except:
            break

    conn.close()

def main():
    # Create IPv4 TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(("0.0.0.0", 5000))   # bind to localhost:5000
    server.listen(2)                 # listen for 2 connections

    print("Server running on port 5000. Waiting for 2 connections...")

    for i in range(2):
        conn, addr = server.accept()
        clients[i] = conn
        print(f"Player {i+1} connected: {addr}")

        # Initial message that is printed
        initial_message = {
            "type": "init",
            "paddle": "left" if i == 0 else "right",
            "screenWidth": 640,
            "screenHeight": 480
        }

        conn.send(json.dumps(initial_message).encode())

    # Start the threads
    for i in range(2):
        t = threading.Thread(target=handle_client, args=(clients[i], i))
        t.start()

if __name__ == "__main__":
    main()



