from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_user_data():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username, num_wins FROM users")
    data = cursor.fetchall()

    conn.close()
    return data

@app.route('/')
def index():
    users_data = get_user_data()
    return render_template('index.html', users=users_data)

if __name__ == '__main__':
    app.run(host='localhost', port=80)

