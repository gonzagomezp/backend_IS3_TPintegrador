import uvicorn
import controller
from fastapi import HTTPException, status,FastAPI
from database import db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    
    db.connect()
    print("RUNNING")

@app.on_event("shutdown")
async def shutdown_event():
    db.disconnect()

@app.post("/user", status_code=status.HTTP_201_CREATED)
async def insert_user(json: dict):
    try:
        username = json.get("username","N/A")
        password = json.get("password","N/A")
        print(json)
        # Lógica para insertar el usuario y obtener el ID
        result = controller.InsertUser(username, password)
        return {"UserId": result} # Devolver el ID del usuario
    except Exception as e:
        # Si ocurre un error, lanzar una excepción HTTP con código de estado 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/user/{username}")
async def get_user(username: str):
    try:
        user = controller.GetUserByUsername(username)
        if user:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users")
async def get_users():
    try:
        users = controller.GetUsers()
        if users:
            return users
        else:
            return "no users in database"
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

