from database import db

def GetUsers():
    # Supongamos que db.get_users() devuelve una lista de tuplas
    # Por ejemplo: [(1, 'user1', 'pass1'), (2, 'user2', 'pass2')]
    users = db.get_users()
    
    # Convertir la tupla en una lista de diccionarios
    users_dict = [{'id': user[0], 'username': user[1], 'password': user[2]} for user in users]
    
    # Imprimir los resultados para verificar
    print(users_dict)
    print(type(users_dict))
    
    return users_dict

def GetUserByUsername(username):
    # Supongamos que db.get_user(username) devuelve una tupla
    # Por ejemplo: (1, 'user1', 'pass1')
    user = db.get_user(username)
    
    # Convertir la tupla en un diccionario
    user_dict = {'id': user[0], 'username': user[1], 'password': user[2]}
    
    return user_dict


def InsertUser(username, password):
    return db.insert_user(username, password)
