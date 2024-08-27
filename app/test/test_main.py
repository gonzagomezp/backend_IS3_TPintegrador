# test_main.py
import os
os.environ["TESTING"] = "true"  # Establecer la variable de entorno antes de importar la app

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Tests para /user (POST)
def test_insert_valid_user():
    response = client.post("/user", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 201
    assert "UserId" in response.json()
    assert response.json()["UserId"] == 1

def test_insert_user_without_username():
    response = client.post("/user", json={"password": "testpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username and password are required"

def test_insert_user_without_password():
    response = client.post("/user", json={"username": "testuser2"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username and password are required"

# Tests para /user/{username} (GET)
def test_get_existing_user():
    response = client.post("/user", json={"username": "testuser", "password": "testpassword"})
    print(f"Insert User Response: {response.json()}")  # Añadido para depuración
    response = client.get("/user/testuser")
    print(f"Get User Response: {response.json()}")  # Añadido para depuración
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_get_non_existing_user():
    response = client.get("/user/nonexistentuser")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Tests para /users (GET)
def test_get_users_with_existing_users():
    client.post("/user", json={"username": "testuser1", "password": "testpassword1"})
    client.post("/user", json={"username": "testuser2", "password": "testpassword2"})
    response = client.get("/users")  # Añadir esta línea para inicializar 'response'
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) >= 2
    
def test_get_users_with_no_users():
    # Necesitas resetear tu base de datos mock aquí si es posible
    response = client.get("/users")
    assert response.status_code == 404
    assert response.json()["detail"] == "No user found in database"

# Tests para /user/{id} (DELETE)
def test_delete_existing_user():
    client.post("/user", json={"username": "testuser", "password": "testpassword"})
    response = client.delete("/user/1")
    print(f"Delete User Response: {response.json()}")  # Añadido para depuración
    assert response.status_code == 200
    assert response.json()["deleted"] == 1

def test_delete_non_existing_user():
    response = client.delete("/user/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "No se encontró ningún usuario con ese ID"

