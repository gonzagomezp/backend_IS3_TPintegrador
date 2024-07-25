import mysql.connector
from fastapi import HTTPException
import requests
from google.auth import compute_engine
import sqlalchemy
from google.cloud.sql.connector import Connector


class MySQLDatabase:
    def __init__(self, database, user, password, production=False): # '/cloudsql/frontend-430223:us-central1:mysql-server'
        self.database = database
        self.user = user
        self.password = password
        self.production = production
        self.connection = None
        self.host = "34.70.233.252"  # para probar localmente
        self.instance_connection_name = 'frontend-430223:us-central1:mysql-server'  # Nombre de la conexión de la instancia de Cloud SQL

    def connect(self):
        if self.production:
            self.connect_production()
        else:
            self.connect_local()

    def connect_production(self):
        try:
            connector = Connector()

            def getconn():
                conn = connector.connect(
                    self.instance_connection_name,
                    "pymysql",
                    user=self.user,
                    password=self.password,
                    db=self.database
                )
                return conn

            pool = sqlalchemy.create_engine(
                "mysql+pymysql://",
                creator=getconn,
            )
            
            self.connection = pool.connect()
            print("Conexión a MySQL en producción establecida")
            self.create_users_table_if_not_exists()
        except Exception as e:
            print("-------------------------------")
            print("DATABASE ERROR")
            print()
            print(f"Error al conectar a MySQL en producción: {e}")
            print()
            print("-------------------------------")
            raise e

    def connect_local(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                print("Conexión a MySQL local establecida")
                self.create_users_table_if_not_exists()
        except Exception as e:
            print("-------------------------------")
            print("DATABASE ERROR")
            print()
            print(f"Error al conectar a MySQL local: {e}")
            print()
            print("-------------------------------")
            raise e

    def create_users_table_if_not_exists(self):
        if self.connection.is_connected() == False:
            print("BASE DE DATOS NO CONECTADA")
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
        except Exception as e:
            print(f"Error al crear la tabla 'users': {e}")
            raise e

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a MySQL cerrada")

    def get_users(self):
        try:
            print("PING")
            if self.connection.is_connected() == False:
                print("BASE DE DATOS NO CONECTADA")
                raise HTTPException(500, "FALLO EN LA CONEXIÓN CON LA BASE DE DATOS")

            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()
            return users
        except Exception as e:
            print(f"Exception al obtener usuarios: {e}")
            raise e

    def get_user(self, username: str):
        try:
            if self.connection.is_connected() == False:
                print("BASE DE DATOS NO CONECTADA")
                raise HTTPException(500, "FALLO EN LA CONEXIÓN CON LA BASE DE DATOS")

            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Exception as e:
            print(f"Exception al obtener usuario: {e}")
            raise e

    def insert_user(self, username: str, password: str):
        try:
            if self.connection.is_connected() == False:
                print("BASE DE DATOS NO CONECTADA")
                raise HTTPException(500, "FALLO EN LA CONEXIÓN CON LA BASE DE DATOS")

            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            return user_id
        except Exception as e:
            print(f"Exception al insertar usuario: {e}")
            self.connection.rollback()
            raise e

# Uso de la clase
db = MySQLDatabase(database='Usuarios', user='root', password='roott', production=True)
db.connect()
