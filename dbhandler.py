import sqlite3
import uuid
import secrets
import hashlib
import datetime

sql = sqlite3.connect('database.db', check_same_thread=False)

def createDBIfNotExists():
    cursor = sql.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, username tinytext, password tinytext, salt tinytext, token text)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS items
                (id INTEGER PRIMARY KEY, owner int, name tinytext, desc tinytext, done bool, created DATETIME)''')
    
    sql.commit()

    cursor.close()

def createSessionID():
    return secrets.token_hex(64)

def createSalt():
    return secrets.token_hex(8)

def hashString(password, salt):
    text = password + str(salt)
    text = bytes(text, "utf-8")
    return hashlib.sha256(text).hexdigest()

def checkIfUsernameTaken(username: str):
    cursor = sql.cursor()

    t = [username]

    cursor.execute('''SELECT * FROM users WHERE username = ?''', t)

    user = cursor.fetchone()

    if user == None:
        return False
    
    return True

def passwordMatches(password: str, username: str):
    cursor = sql.cursor()

    t = [username]

    cursor.execute('''SELECT salt FROM users WHERE username = ?''', t)
    salt = cursor.fetchone()

    if not salt:
        return False
    
    salt = salt[0]

    cursor.close()

    hashedPassword = hashString(password, salt)

    cursor = sql.cursor()

    t = [hashedPassword]

    cursor.execute('''SELECT username FROM users WHERE password = ?''', t)
    user = cursor.fetchone()

    if not user:
        return False
    
    user = user[0]

    cursor.close()

    if user == username:
        return True
    
    return False

def createUser(username, password):
    cursor = sql.cursor()

    token = createSessionID()
    salt = createSalt()
    hash = hashString(password, salt)
    hashedToken = hashString(token, "")

    t = [username, hash, hashedToken, salt]

    cursor.execute('''INSERT INTO users (username, password, token, salt) VALUES (?, ?, ?, ?)''', t)
    sql.commit()
    cursor.close()

    return token

def createTask(token: str, name: str, desc: str):
    cursor = sql.cursor()

    id = getUserInfoFromToken(token)[0]

    t = [id, name, desc]

    cursor.execute('''INSERT INTO items (owner, name, desc, done, created) VALUES (?, ?, ?, 0, datetime('now', 'localtime'))''', t)
    sql.commit()
    cursor.close()

    return {"name": name, "desc": desc}

def loginUser(username: str):
    cursor = sql.cursor()

    token = createSessionID()
    hashedToken = hashString(token, "")

    t = [hashedToken, username]

    cursor.execute('''UPDATE users SET token = ? WHERE username = ?''', t)
    sql.commit()
    cursor.close()

    return token

def getUserInfoFromToken(token: str):
    cursor = sql.cursor()

    hashedToken = hashString(token, "")

    t = [hashedToken]
    cursor.execute('''SELECT * FROM users WHERE token = ?''', t)
    user = cursor.fetchone()
    cursor.close()

    return user

def getItems(token: str, amount: int, offset: int, order: str, search: str, done: int):
    if getUserInfoFromToken(token):

        cursor = sql.cursor()

        id = getUserInfoFromToken(token)[0]

        searchq = search
        if search == "!" or not search:
            searchq = ""

        orderq = order.upper()
        if order.lower() != "desc" or order.lower() != "asc":
            orderq = "DESC"
        
        doneCommand = ""
        
        t = [id, f"%{searchq}%", amount, offset]

        doneq = done
        if done == 0 or done == 1:
            doneCommand = f"AND done = {doneq}"
            

        cursor.execute(f'''SELECT * FROM items
                       WHERE owner = ? {doneCommand} AND name LIKE ?
                       ORDER BY id {orderq}
                       LIMIT ? OFFSET ?
                       ''', t)
        
        items = cursor.fetchall()
        cursor.close()

        return items

def getItem(token: str, id: int):
    if getUserInfoFromToken(token):

        cursor = sql.cursor()

        ownerid = getUserInfoFromToken(token)[0]

        t = [ownerid, id]

        cursor.execute('''SELECT * FROM items
                       WHERE owner = ? AND id = ?
                       ''', t)
        
        items = cursor.fetchone()
        cursor.close()

        return items

def deleteItem(token: str, id: int):

    if getItem(token, id):
        cursor = sql.cursor()

        ownerid = getUserInfoFromToken(token)[0]

        t = [ownerid, id]

        cursor.execute('''DELETE FROM items
                       WHERE owner = ? AND id = ?
                       ''', t)
        sql.commit()
        cursor.close()

        return True


    return False

def checkItem(token: str, id: int):
    if getItem(token, id):
        cursor = sql.cursor()

        ownerid = getUserInfoFromToken(token)[0]

        t = [ownerid, id]

        cursor.execute('''SELECT done FROM items
                       WHERE owner = ? AND id = ?
                       ''', t)
        done = cursor.fetchone()

        print(done[0])

        check = 1
        if done[0] == 1:
            check = 0

        t = [check, ownerid, id]

        cursor.execute('''UPDATE items
                       SET done = ?
                       WHERE owner = ? AND id = ?
                       ''', t)

        sql.commit()
        cursor.close()

        return True


    return False