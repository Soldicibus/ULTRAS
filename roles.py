import sqlite3



def create_db():
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level INTEGER,
            experience INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def get_user_id_by_username(username):
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    
    result = cursor.fetchone()
    
    if result:
        user_id = result[0]
    else:
        user_id = None

    conn.close()
    return user_id


def add_user(user_id, username):
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    cursor.execute('''
        INSERT INTO users (user_id, username, level, experience)
        VALUES (?, ?, 1, 0)
    ''', (user_id, username))

    conn.commit()
    conn.close()


def update_user_level(user_id, new_level):
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE users
        SET level = level+1,
            experience = 0
        WHERE user_id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()

def update_user_exp(user_id):
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE users
        SET experience = experience+1
        WHERE user_id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    conn.close()

    return user

create_db()
