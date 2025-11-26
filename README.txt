Contact Info
============

Group Members & Email Addresses:

    Nathan Edwards, cned224@uky.edu

Versioning
==========

Github Link: https://github.com/nathane28/pongProject

General Info
============
This file describes how to install/run your program and anything else you think the user should know

Install Instructions
====================

Run the following line to install the required libraries for this project:

`pip3 install -r requirements.txt`
- Make sure pygame is installed on your PC before continuing
- If not already downloaded, download project files, more specifically the files "pongServer.py" and "pongClient.py"
- Remember what folder/directory these files are located and open either VS Code with a Terminal, Windows Terminal, or Windows Powershell
- Navigate to the folder/directory the files are located in
- Either coordinating with another person with the files on their PC and/or running a split terminal, the files "pongClient.py" and "pongServer.py" should be run seperately
- For both files, they are ran with the commands
    - py pongClient.py
    - py pongServer.py
- The "pongServer.py" file needs to be ran first. Initializing and Starting the server. A message stating "Server running on Port 5000. Waiting for 2 connections..." should be displayed
- Once that message is displayed, the "pongClient.py" file needs to be ran with the command above. A pygame UI will display on the screen with options to put in a Server IP and Port
- Enter the server ID and Server Port to connect to the Server, in this case the IP is "127.0.0.1" and Port 5000 since it is ran locally (in testing)
- Once the two clients enter the Server information, the game will start on the screen.

Known Bugs
==========
- Not sure if clients can even play against each other in the same game, etc.
- Terminal that launches the server side code never exits, and has to be restarted every time a new game wants to be played, or the server needs to be re-launched


