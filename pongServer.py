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
import time

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

# Shared game state
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
ballVX = 4
ballVY = 4
WIDTH, HEIGHT = 640, 480
PADDLE_HEIGHT = 50
PADDLE_WIDTH = 10

# -------------------- Handle paddle updates --------------------
def handle_client(conn, player_id):
    global game_state
    while True:
        try:
            raw = conn.recv(1024)
            if not raw:
                break
            data = json.loads(raw.decode())
            if player_id == 0:
                game_state["leftpaddle"] = data["paddleY"]
            else:
                game_state["rightpaddle"] = data["paddleY"]
            game_state["sync"][player_id] = data["sync"]
        except Exception as e:
            print(f"SERVER ERROR player {player_id}: {e}")
            break
    conn.close()
    clients[player_id] = None

# -------------------- Broadcast to clients --------------------
def broadcast(msg):
    for i, c in enumerate(clients):
        if c:
            try:
                c.send(json.dumps(msg).encode())
            except:
                clients[i] = None

# -------------------- Server game loop --------------------
def server_game_loop():
    global game_state, ballVX, ballVY
    while True:
        # Update ball
        game_state["ballX"] += ballVX
        game_state["ballY"] += ballVY

        # Top/bottom collision
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

        # Broadcast updated state
        broadcast(game_state)
        time.sleep(1/60)  # 60 FPS

def reset_ball():
    global game_state, ballVX, ballVY
    game_state["ballX"] = WIDTH // 2
    game_state["ballY"] = HEIGHT // 2
    ballVX = -ballVX
    ballVY = 4

# -------------------- Accept clients --------------------
def accept_clients(server):
    i = 0
    while i < 2:
        conn, addr = server.accept()
        clients[i] = conn
        print(f"Player {i+1} connected: {addr}")

        initial_message = {
            "type": "init",
            "paddle": "left" if i == 0 else "right",
            "screenWidth": WIDTH,
            "screenHeight": HEIGHT
        }
        conn.send(json.dumps(initial_message).encode())

        threading.Thread(target=handle_client, args=(conn, i), daemon=True).start()
        i += 1

# -------------------- Main --------------------
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen(2)
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



