# test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Tests
def test_insert_user():
    response = client.post("/user", json={"username": "testuser", "password": "testpassword"})
    print(response.json())  # Verifica la respuesta capturada
    assert response.status_code == 201
    assert "UserId" in response.json()
    assert response.json()["UserId"] == 1  # Asumiendo que el ID de usuario esperado es 1
