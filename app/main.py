#main.py
import os
import uvicorn
from fastapi import HTTPException, status, FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.database import db  # Importar la base de datos real
from .test.mocks import MockMySQLDatabase  # Importar la base de datos simulada

def get_db():
    if os.getenv("TESTING") == "true":
        return MockMySQLDatabase()
    return db

@asynccontextmanager # Context manager para el ciclo de vida de la aplicación
async def lifespan(app: FastAPI):
    db_instance = get_db()
    try:
        db_instance.connect()  # Intentar conectar a la base de datos
        print("Database connection established")
        yield
    finally:
        db_instance.disconnect()  # Desconectar de la base de datos al cerrar la aplicación
        print("Database connection closed")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def hello_world():
    return {
        "Hello World": "This is a FastAPI application"
    }

@app.post("/user", status_code=status.HTTP_201_CREATED)
async def insert_user(json: dict):
    try:
        db_instance = get_db()
        username = json.get("username")
        password = json.get("password")
        if not username or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")   
        print(json)
        # Lógica para insertar el usuario y obtener el ID
        result = db_instance.insert_user(username, password)
        return {"UserId": result}  # Devolver el ID del usuario
    except Exception as e:
        # Si ocurre un error, lanzar una excepción HTTP con código de estado 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/user/{username}")
async def get_user(username: str):
    try:
        db_instance = get_db()
        user = db_instance.get_user(username)
        if user:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except HTTPException as xp:
        raise xp
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users")
async def get_users():
    try:
        db_instance = get_db()
        users = db_instance.get_users()
        if users:
            return users
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found in database")
    except HTTPException as xp:
        raise xp
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete("/user/{id}")
async def delete_user(id: int):
    try:
        db_instance = get_db()
        deleted = db_instance.delete_user(id)
        if deleted:
            return {"deleted": deleted}
        else:
            raise HTTPException(status_code=404, detail="No se encontró ningún usuario con ese ID")
    except HTTPException as xp:
        raise xp
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
