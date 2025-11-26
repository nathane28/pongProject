# =================================================================================================
# Contributing Authors:	    Nathan Edwards
# Email Addresses:          nathan.edwards281@uky.edu
# Date:                     November 25th, 2025
# Purpose:                  This file will contain all of the server side logic to work with the client
#                           side to make sure the pong game all works correctly with all parts 
#                           flowing together to correctly operate.
# Misc:                     
# =================================================================================================

import socket
import threading
import json
import time
from typing import Any, Dict

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

# Shared game state that the clietns will recieve every frame sent
game_state = {
    "leftpaddle": 215,
    "rightpaddle": 215,
    "ballX": 320,
    "ballY": 240,
    "lScore": 0,
    "rScore": 0,
    "sync": [0,0]
}

clients = [None, None]

# Ball velocity of pygame
ballVX = 4
ballVY = 4

# Width of the field for pygame
WIDTH, HEIGHT = 640, 480
PADDLE_HEIGHT = 50
PADDLE_WIDTH = 10

# Author: Nathan Edwards
# Purpose: The purpose of this function is to recieve data from the clients that are connected to the server and update the state of the game
#          based on the information that is recieved from the clients to track each clients paddle position, the score of the game, etc.
# Pre-Conditions: Pre-conditions would include that the socket connection is active and sucessfully connected, the game_state is already initialized,
#                 along with the player_id.
# Post-Conditions: The server game_state is updated as a post-condition based on the data that is recieved from the clients, as well as the chance
#                  that there is a network server error
# def handle_client(conn: socket.socket(), player_id: int) -> None:
def handle_client(conn, player_id):
    global game_state

    # While loop that continues unless there is a network error
    while True:
        try:
            raw = conn.recv(1024)

            if not raw:
                break

            data = json.loads(raw.decode())

            # Update the paddle according to which player it is
            if player_id == 0:
                game_state["leftpaddle"] = data["paddleY"]
            else:
                game_state["rightpaddle"] = data["paddleY"]

            game_state["sync"][player_id] = data["sync"]

        # Error exception
        except Exception as e:
            print(f"SERVER ERROR player {player_id}: {e}")
            break

    conn.close()    # Connection is closed

    clients[player_id] = None   # Clients are disconnected

# Author: Nathan Edwards
# Purpose: Broadcast the game_state to all of the clients so that the game can be synchronized
# Pre-Conditions: All of the connections between the server and client are valid and active, and the server and client are able to communicate
#                 effectively.
# Post-Conditions: All of the clients recieve the messages that are "broadcasted", ensuring that the game between the two clients stay as 
#                  synchronized as possible, etc.
# def broadcast(msg: Dict[str, Any]) -> None:
def broadcast(msg):
    for i, c in enumerate(clients):
        if c:
            try:
                c.send(json.dumps(msg).encode())
            except:
                clients[i] = None

# Author: Nathan Edwards
# Purpose: Main loop of the server used to update the game state allowing the game to sucessfully continue between the two clients.
# Pre-Conditions: Game_state is initilialized and valid, with all of the values regarding the ball and paddles are all correct and error free.
# Post-Conditions: All of the values regarding the ball and paddles are updated, along with the potential score based on the actions of the two
#                  clients playing in the game.
# def server_game_loop() -> None:
def server_game_loop():
    global game_state, ballVX, ballVY

    while True:
        # Moving the ball
        game_state["ballX"] += ballVX
        game_state["ballY"] += ballVY

        # Collision with top/bottom walls
        if game_state["ballY"] <= 0 or game_state["ballY"] >= HEIGHT:
            ballVY = -ballVY

        # Left paddle collision
        if game_state["ballX"] <= PADDLE_WIDTH + 10:
            if game_state["leftpaddle"] <= game_state["ballY"] <= game_state["leftpaddle"] + PADDLE_HEIGHT:
                ballVX = -ballVX
            else:
                game_state["rScore"] += 1
                reset_ball()

        # Right paddle collision
        if game_state["ballX"] >= WIDTH - PADDLE_WIDTH - 10:
            if game_state["rightpaddle"] <= game_state["ballY"] <= game_state["rightpaddle"] + PADDLE_HEIGHT:
                ballVX = -ballVX
            else:
                game_state["lScore"] += 1
                reset_ball()

        # Broadcast updated state to both clients
        broadcast(game_state)  

# Author: Nathan Edwards
# Purpose: Reset the ball to the center of the screen after a point is scored. Made to help the disconnect between the clients attempting to play
#          against each other
# Pre-Conditions: The game_state is valid and a point is scored by one of the clients playing in the game
# Post-Conditions: The ball is reset and placed back into the center of the screen
# def reset_ball() -> None:
def reset_ball():
    global game_state, ballVX, ballVY

    # Center the ball like the start
    game_state["ballX"] = WIDTH // 2
    game_state["ballY"] = HEIGHT // 2
    ballVX = -ballVX
    ballVY = 4

# Author: Nathan Edwards
# Purpose: Waits for two clients to connect to the server and assigns them each a "left" or "right" paddle, along with initializing the start of the
#          game. It also starts a thread to handle the updates that will occur between the clients and server and sends an initial packet to each client
# Pre-Conditions: The two clients are connecting or already connected to the server through the correct IP address and port
# Post-Conditions: Both of the clients are successfully connected to the server, each assigned a side/paddle for the game, and are completely ready 
#                  to start the game and play against each other, etc.
# def accept_clients(server: socket.socket) -> None:
def accept_clients(server):
    i = 0

    # While loop that only continues when there is 2 players
    # Since only 2 players are allowed to play
    while i < 2:

        # Accept a new client to connect to the server
        conn, addr = server.accept()
        clients[i] = conn

        # Display which player has succesfully connected to the server
        print(f"Player {i+1} connected: {addr}")

        # Initialize each client to which side/paddle they are in the game
        initial_message = {
            "type": "init",
            "paddle": "left" if i == 0 else "right",
            "screenWidth": WIDTH,
            "screenHeight": HEIGHT
        }

        # Send the configuration for each client connecting
        conn.send(json.dumps(initial_message).encode())

        # A thread is started to try and keep track of paddle movement
        threading.Thread(target=handle_client, args=(conn, i), daemon=True).start()
        i += 1

# Author: Nathan Edwards
# Purpose: This is the main function that sets up and creates the server/socket for the game to be run on and accept exactly two client connections
#          for the two players that will be playing against each other in the game of Pong
# Pre-Conditions: The server socket is ready to be started, and ready to listen to the connections of the clients playing
# Post-Conditions: The server is fully operational, and is ready to start the game, the clients are connected, and everything is operating smoothly
#                  for the clients to begin playing, and for them to be able to communicate between the server and themselves smoothly the entirety
#                  of the game.
# def main() -> None:
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create the socket
    server.bind(("0.0.0.0", 5000))                              # Bind to the local host, port 5000
    server.listen(2)                                            # Server needs to listen for 2 connections from each of the player clients

    # Message printed out when the server starts running
    print("Server running on port 5000. Waiting for 2 connections...")

    # Accept clients
    accept_clients(server)

    # Start server game loop
    threading.Thread(target=server_game_loop, daemon=True).start()

    # Keep server alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()



