import uvicorn
import controller
from fastapi import HTTPException, status,FastAPI
from database import db

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    
    db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    db.disconnect()

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
        "title": "A Melancholy Farewell",
        "line1": "In the vast expanse of digital realms,",
        "line2": "We stand at the edge of a bittersweet departure.",
        "line3": "Here, we whisper our goodbye to the mundane,",
        "line4": "And embrace the beauty of fleeting moments.",
        "line5": "So, with a gentle sigh, we say:",
        "line6": "'Bye bye, cruel world!'",
        "line7": "May your adventures be filled with wonder and joy."
    }

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
    except HTTPException as xp:
        raise xp
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users")
async def get_users():
    try:
        users = controller.GetUsers()
        if users:
            return users
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found in database")
    except HTTPException as xp:
        raise xp
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


