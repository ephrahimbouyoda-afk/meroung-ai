import sqlite3


def init_db():
    conn = sqlite3.connect('meroung_ai.db')
    c = conn.cursor()
    # Table des utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT, 
                  solde_credits INTEGER DEFAULT 5)''')

    # Table des messages
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER, 
                  role TEXT, 
                  content TEXT, 
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()


def verifier_credits(username):
    conn = sqlite3.connect('meroung_ai.db')
    c = conn.cursor()
    c.execute("SELECT solde_credits FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0


def decrementer_credit(username):
    conn = sqlite3.connect('meroung_ai.db')
    c = conn.cursor()
    c.execute("UPDATE users SET solde_credits = solde_credits - 1 WHERE username = ? AND solde_credits > 0",
              (username,))
    conn.commit()
    conn.close()


init_db()
