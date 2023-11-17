# =================================================================================================
# Contributing Authors:	    Kevin Cosby, Oskar Flores 
# Email Addresses:          knco259@uky.edu, oskar.flores@uky.edu
# Date:                     2023 November 15
# Purpose:                  handles serving the leaderboard on localhost:80
# Misc:                     Released under GNU GPL v3.0
# =================================================================================================

from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_user_data():
    # =========================================
    # Author: Kevin Cosby, Oskar Flores
    # Purpose: gets user data from the database
    # pre: valid database exists
    # post: returns the username/num_wins columns
    # =========================================
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # get usernames and wins
    cursor.execute("SELECT username, num_wins FROM users")
    data = cursor.fetchall()

    conn.close()
    return data

@app.route('/')
def index():
    # =========================================
    # Author: Kevin Cosby, Oskar Flores
    # Purpose: displays leaderboard on http://localhost:80
    # pre: valid database exists, script was run with sudo (depending on your configuration)
    # post: website is served on http://localhost:80
    # =========================================
    users_data = get_user_data()
    return render_template('index.html', users=users_data)

if __name__ == '__main__':
    app.run(host='localhost', port=80)

