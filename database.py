import mysql.connector
from mysql.connector import Error
import os

class MySQLDatabase:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                print("Conexión a MySQL establecida")
                self.create_users_table_if_not_exists()
        except Error as e:
            print("-------------------------------")
            print("DATABASE ERROR")
            print()
            print(f"Error al conectar a MySQL: {e}")
            print()
            print("-------------------------------")
            raise e
        
    def create_users_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            password VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL UNIQUE
        )
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            cursor.close()
            print("Tabla 'users' creada o ya existe")
        except Error as e:
            print(f"Error al crear la tabla 'users': {e}")
            raise e

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a MySQL cerrada")
    
    def get_users(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()
            return users
        except Error as e:
            print(f"Error al obtener usuarios: {e}")
            raise e

    def get_user(self, username: str):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error al obtener usuario: {e}")
            raise e

    def insert_user(self, username: str,  password: str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            return user_id
        except Error as e:
            print(f"Error al insertar usuario: {e}")
            self.connection.rollback()
            raise e
        
# Uso de la clase
db = MySQLDatabase(host=os.getenv("HOST"), database='Usuarios', user='root', password='roott')
