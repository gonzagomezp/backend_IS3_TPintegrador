from google.cloud.sql.connector import Connector
import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException

class MySQLDatabase:
    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        try:
            connector = Connector()
            self.connection = connector.connect(
                "ingenieriadesoftware3:us-central1:mysql-server",
                "pymysql",
                user=self.user,
                password=self.password,
                db=self.database
            )
                
            print()
            print(self.connection)
            print()
            print("Conexión a MySQL establecida")
            self.create_users_table_if_not_exists()
        except Exception as e:
            print("-------------------------------")
            print("DATABASE ERROR")
            print()
            print(f"Error al conectar a MySQL: {e}")
            print()
            print("-------------------------------")

    def create_users_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(32) NOT NULL UNIQUE,
            password VARCHAR(32) NOT NULL
            );
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
        if self.connection:
            self.connection.close()
            print("Conexión a MySQL cerrada")
    
    def get_users(self):
        try:
            if self.connection == False:
                print ("BASE DE DATOS NO CONECTADA")
                raise HTTPException(500, "FALLO EN LA CONEXCION CON LA BASE DE DATOS")
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()
            return users
        except Error as e:
            print(f"Error al obtener usuarios: {e}")
            raise e

    def get_user(self, username: str):
        try:
            if self.connection == False:
                print ("BASE DE DATOS NO CONECTADA")
                raise HTTPException(500, "FALLO EN LA CONEXCION CON LA BASE DE DATOS")
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error al obtener usuario: {e}")
            raise e

    def insert_user(self, username: str, password: str):
        try:
            if self.connection == False:
                print ("BASE DE DATOS NO CONECTADA")
                raise HTTPException(500, "FALLO EN LA CONEXCION CON LA BASE DE DATOS")
                   
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

    def delete_user(self, idd: int):
        try:
            if self.connection == False:
                print ("BASE DE DATOS NO CONECTADA")
                raise HTTPException(500, "FALLO EN LA CONEXCION CON LA BASE DE DATOS")
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (idd,))
            self.connection.commit()
            deleted = cursor.rowcount
            cursor.close()
            
            #devolver True si se eliminó al menos un usuario, False en caso contrario
            return deleted > 0
        except Error as e:
            print(f"Error al eliminar usuario: {e}")
            self.connection.rollback()
            raise e
    
# Uso de la clase
db = MySQLDatabase(database='Usuarios', user='root', password='roott')
