import os
from google.cloud.sql.connector import Connector
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class MySQLDatabase:
    def __init__(self):
        self.db_user = "root"
        self.db_pass = "roott"
        self.db_name = "Usuarios"
        self.cloud_sql_instance = "frontend-430223:us-central1:mysql-server"
        self.connector = Connector()
        self.engine = None

    def getconn(self):
        return self.connector.connect(
            self.cloud_sql_instance,
            "pymysql",
            user=self.db_user,
            password=self.db_pass,
            db=self.db_name
        )

    def connect(self):
        try:
            if self.engine is None:
                self.engine = create_engine(
                    "mysql+pymysql://",
                    creator=self.getconn,
                )
            with self.engine.connect() as connection:
                print("Conexión a MySQL establecida")
                self.create_users_table_if_not_exists(connection)
        except SQLAlchemyError as e:
            print("-------------------------------")
            print("DATABASE ERROR")
            print()
            print(f"Error al conectar a MySQL: {e}")
            print()
            print("-------------------------------")
            raise e

    def create_users_table_if_not_exists(self, connection):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            password VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL UNIQUE
        )
        """
        try:
            connection.execute(text(create_table_query))
            print("Tabla 'users' creada o ya existe")
        except SQLAlchemyError as e:
            print(f"Error al crear la tabla 'users': {e}")
            raise e

    def disconnect(self):
        if self.engine is not None:
            self.engine.dispose()
            print("Conexión a MySQL cerrada")

    def get_users(self):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT * FROM users"))
                users = result.fetchall()
                return users
        except SQLAlchemyError as e:
            print(f"Error al obtener usuarios: {e}")
            raise e

    def get_user(self, username: str):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("SELECT * FROM users WHERE username = :username"), {'username': username}
                )
                user = result.fetchone()
                return user
        except SQLAlchemyError as e:
            print(f"Error al obtener usuario: {e}")
            raise e

    def insert_user(self, username: str, password: str):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("INSERT INTO users (username, password) VALUES (:username, :password)"), {'username': username, 'password': password}
                )
                user_id = result.lastrowid
                connection.commit()
                return user_id
        except SQLAlchemyError as e:
            print(f"Error al insertar usuario: {e}")
            raise e

# Uso de la clase
db = MySQLDatabase()