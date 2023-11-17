Contact Info
============

Group Members & Email Addresses:

    Person 1, knco259@uky.edu
    Person 2, oskar.flores@uky.edu 

Versioning
==========

Github Link: https://github.com/KevinCPP/Multiplayer-Pong

General Info
============
To view the leaderboard on `http://localhost:80`, run `sudo python3 leaderboard.py`. This pulls directly from the users.db database and displays
the usernames and the wins. The reason it needs root privileges is because ports <1024 usually require root, and the assignment requires port 80.

If you simply type `localhost:80` into your browser, or `https://localhost:80`, it will not work and you may receive an error. Only use `http` not
`https`. 

Features
========
- Fully implemented pong client and pong server
- Supports multiple simultaneous games with multiple pairs of players, using the GameID system.
- Performs password checking and user verification. If the user doesn't exist, it effectively creates an account for them. If it does exist, it compares the hashed password to the one in the db.
- Users can "replay" the game if both press the Enter key on the win screen
- users and their wins are tracked and displayed on `http://localhost:80` when running the `leaderboard.py` script.

Install Instructions
====================

Run the following line to install the required libraries for this project:

`pip3 install -r requirements.txt`


Known Bugs
==========
- GameIDs cannot be reused without restarting the server. However, we would probably use a randomized hash for this anyways rather than using a simple string like "1", but we did that for convenience sake.
