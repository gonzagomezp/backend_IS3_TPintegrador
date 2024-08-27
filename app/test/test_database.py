# tests/test_database.py


"""

Explicación de los Tests
Fixtures de Pytest:

@pytest.fixture: Define una instancia de MySQLDatabase que se reutiliza en múltiples tests.
Mocks:

@patch('database.Connector'): Simula la clase Connector de google.cloud.sql.connector para evitar conexiones reales.
MagicMock(): Crea objetos simulados para connection y cursor.
Tests de Conexión:

test_connect_success: Verifica que la conexión se establezca correctamente y que se llame al método para crear la tabla de usuarios.
test_connect_failure: Simula una falla en la conexión y verifica que se lance una excepción.
Tests de Creación de Tabla:

test_create_users_table_if_not_exists_success: Verifica que la tabla se cree correctamente.
test_create_users_table_if_not_exists_failure: Simula un error al crear la tabla y verifica que se lance una excepción.
Test de Desconexión:

test_disconnect: Verifica que la conexión se cierre correctamente.
Tests de Obtención de Usuarios:

test_get_users_success: Verifica que se obtengan los usuarios correctamente.
test_get_users_not_connected: Verifica que se lance una excepción si la conexión no está establecida.
test_get_users_error: Simula un error al obtener usuarios y verifica que se lance una excepción.
Tests de Obtención de un Usuario Específico:

test_get_user_success: Verifica que se obtenga un usuario específico correctamente.
test_get_user_not_connected: Verifica que se lance una excepción si la conexión no está establecida.
test_get_user_error: Simula un error al obtener un usuario y verifica que se lance una excepción.
Tests de Inserción de Usuarios:

test_insert_user_success: Verifica que un usuario se inserte correctamente y que se obtenga el user_id.
test_insert_user_not_connected: Verifica que se lance una excepción si la conexión no está establecida.
test_insert_user_error: Simula un error al insertar un usuario y verifica que se lance una excepción y se realice un rollback.
Tests de Eliminación de Usuarios:

test_delete_user_success: Verifica que un usuario se elimine correctamente.
test_delete_user_no_deletion: Verifica el comportamiento cuando no se elimina ningún usuario.
test_delete_user_not_connected: Verifica que se lance una excepción si la conexión no está establecida.
test_delete_user_error: Simula un error al eliminar un usuario y verifica que se lance una excepción y se realice un rollback.

"""

import pytest
from unittest.mock import MagicMock, patch
from app.database import MySQLDatabase
from mysql.connector import Error
from fastapi import HTTPException

@pytest.fixture
def db():
    return MySQLDatabase(database='test_db', user='test_user', password='test_pass')

# Test del método connect - éxito
@patch('database.Connector')
def test_connect_success(mock_connector, db):
    mock_connection = MagicMock()
    mock_connector.return_value.connect.return_value = mock_connection
    
    with patch.object(db, 'create_users_table_if_not_exists') as mock_create_table:
        db.connect()
        mock_connector.return_value.connect.assert_called_with(
            "frontend-430223:us-central1:mysql-server",
            "pymysql",
            user='test_user',
            password='test_pass',
            db='test_db'
        )
        assert db.connection == mock_connection
        mock_create_table.assert_called_once()

# Test del método connect - falla
@patch('database.Connector')
def test_connect_failure(mock_connector, db):
    mock_connector.return_value.connect.side_effect = Error("Connection failed")
    
    with pytest.raises(Error) as exc_info:
        db.connect()
    assert "Connection failed" in str(exc_info.value)

# Test del método create_users_table_if_not_exists - éxito
def test_create_users_table_if_not_exists_success(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    db.create_users_table_if_not_exists()
    mock_connection.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(32) NOT NULL UNIQUE,
                password VARCHAR(32) NOT NULL
                );
            """)
    mock_cursor.close.assert_called_once()

# Test del método create_users_table_if_not_exists - falla
def test_create_users_table_if_not_exists_failure(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Error("Execute failed")
    mock_connection.cursor.return_value = mock_cursor
    
    with pytest.raises(Error) as exc_info:
        db.create_users_table_if_not_exists()
    assert "Execute failed" in str(exc_info.value)
    mock_cursor.close.assert_called_once()

# Test del método disconnect
def test_disconnect(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    db.disconnect()
    mock_connection.close.assert_called_once()
    # Opcional: Si deseas que connection se establezca a None después de desconectar, modifica el método disconnect
    # assert db.connection is None

# Test del método get_users - éxito
def test_get_users_success(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [('user1', 'pass1'), ('user2', 'pass2')]
    
    users = db.get_users()
    mock_connection.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT * FROM users")
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert users == [('user1', 'pass1'), ('user2', 'pass2')]

# Test del método get_users - base de datos no conectada
def test_get_users_not_connected(db):
    db.connection = False
    with pytest.raises(HTTPException) as exc_info:
        db.get_users()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "FALLO EN LA CONEXCION CON LA BASE DE DATOS"

# Test del método get_users - error al obtener usuarios
def test_get_users_error(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Error("Fetch failed")
    mock_connection.cursor.return_value = mock_cursor
    
    with pytest.raises(Error) as exc_info:
        db.get_users()
    assert "Fetch failed" in str(exc_info.value)
    mock_cursor.close.assert_called_once()

# Test del método get_user - éxito
def test_get_user_success(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ('user1', 'pass1')
    
    user = db.get_user('user1')
    mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE username = %s", ('user1',))
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert user == ('user1', 'pass1')

# Test del método get_user - base de datos no conectada
def test_get_user_not_connected(db):
    db.connection = False
    with pytest.raises(HTTPException) as exc_info:
        db.get_user('user1')
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "FALLO EN LA CONEXCION CON LA BASE DE DATOS"

# Test del método get_user - error al obtener usuario
def test_get_user_error(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Error("Fetch user failed")
    mock_connection.cursor.return_value = mock_cursor
    
    with pytest.raises(Error) as exc_info:
        db.get_user('user1')
    assert "Fetch user failed" in str(exc_info.value)
    mock_cursor.close.assert_called_once()

# Test del método insert_user - éxito
def test_insert_user_success(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 1
    
    user_id = db.insert_user('user1', 'pass1')
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        ('user1', 'pass1')
    )
    mock_connection.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert user_id == 1

# Test del método insert_user - base de datos no conectada
def test_insert_user_not_connected(db):
    db.connection = False
    with pytest.raises(HTTPException) as exc_info:
        db.insert_user('user1', 'pass1')
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "FALLO EN LA CONEXCION CON LA BASE DE DATOS"

# Test del método insert_user - error al insertar usuario
def test_insert_user_error(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Error("Insert failed")
    mock_connection.cursor.return_value = mock_cursor
    
    with pytest.raises(Error) as exc_info:
        db.insert_user('user1', 'pass1')
    assert "Insert failed" in str(exc_info.value)
    mock_connection.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()

# Test del método delete_user - éxito (usuario eliminado)
def test_delete_user_success(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value = mock_cursor
    
    result = db.delete_user(1)
    mock_cursor.execute.assert_called_once_with("DELETE FROM users WHERE id = %s", (1,))
    mock_connection.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert result == True

# Test del método delete_user - ningún usuario eliminado
def test_delete_user_no_deletion(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    
    result = db.delete_user(1)
    mock_cursor.execute.assert_called_once_with("DELETE FROM users WHERE id = %s", (1,))
    mock_connection.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert result == False

# Test del método delete_user - base de datos no conectada
def test_delete_user_not_connected(db):
    db.connection = False
    with pytest.raises(HTTPException) as exc_info:
        db.delete_user(1)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "FALLO EN LA CONEXCION CON LA BASE DE DATOS"

# Test del método delete_user - error al eliminar usuario
def test_delete_user_error(db):
    mock_connection = MagicMock()
    db.connection = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Error("Delete failed")
    mock_connection.cursor.return_value = mock_cursor
    
    with pytest.raises(Error) as exc_info:
        db.delete_user(1)
    assert "Delete failed" in str(exc_info.value)
    mock_connection.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()
