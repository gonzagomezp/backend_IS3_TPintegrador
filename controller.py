from database import db

def GetUsers():
    return db.get_users()

def GetUserByUsername(username):
    return db.get_user(username)

def InsertUser(username, password):
    return db.insert_user(username, password)
