#main.py
import os
import uvicorn
from fastapi import HTTPException, FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.database import db  # Importar la base de datos real
from app.test.mocks import MockModel  # Importar la base de datos simulada

def get_db():
    if os.getenv("TESTING") == "true":
        return MockModel()
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
    db_instance = get_db()
    if type(db_instance).__name__ == "MockModel":
        return {
            "Hello World": "This is a FastAPI API with a mock database"
        }
    return {
        "Hello World": "This is a FastAPI API with a real database"
    }

@app.post("/user", status_code=201)
async def insert_user(json: dict):
    try:
        db_instance = get_db()
        username = json.get("username", None)
        password = json.get("password", None)
        if not username or not password:
            raise HTTPException(400, "Username and password are required")   
        # Lógica para insertar el usuario y obtener el ID
        result = db_instance.insert_user(username, password)
        return {"UserId": result}  # Devolver el ID del usuario
    except HTTPException as xp:
        # Si ocurre una excepción HTTP, lanzarla de nuevo
        print("HTTPexception >>",xp.detail)
        raise xp
    except Exception as e:
        # Si ocurre un error, lanzar una excepción HTTP con código de estado 500
        raise HTTPException(500, detail=str(e))

@app.get("/user/{username}")
async def get_user(username: str):
    try:
        db_instance = get_db()
        user = db_instance.get_user(username)
        if user:
            user_dict = {}
            user_dict["id"] = user[0]
            user_dict["username"] = user[1]
            user_dict["password"] = user[2]
            return user_dict
        else:
            raise HTTPException(404, detail="User not found")
    except HTTPException as xp:
        raise xp
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/users")
async def get_users():
    try:
        db_instance = get_db()
        users = db_instance.get_users()
        if users:
            userss = []
            for user in users:
                u = {}
                u["id"] = user[0]
                u["username"] = user[1]
                u["password"] = user[2]
                userss.append(u)
            return userss
        else:
            raise HTTPException(404, detail="No user found in database")
    except HTTPException as xp:
        raise xp
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.delete("/user/{id}")
async def delete_user(id: int):
    try:
        db_instance = get_db()
        deleted = db_instance.delete_user(id)
        if deleted:
            return {"deleted": deleted}
        else:
            raise HTTPException(404, detail="No se encontró ningún usuario con ese ID")
    except HTTPException as xp:
        raise xp
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
