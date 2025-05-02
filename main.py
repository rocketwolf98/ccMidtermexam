from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date

from sqlalchemy import create_engine, inspect
from sqlalchemy import text

import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL= os.getenv("DATABASE_URL") 
engine = create_engine(DATABASE_URL,  client_encoding='utf8')

try:
    with engine.connect() as test_conn:
        test_conn.execute(text("SELECT 1"))
except Exception as e:
    print(f"Error connecting to database {e}")
    raise

ins = inspect(engine)

try:
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL);
        
        CREATE TABLE IF NOT EXISTS tasks(
            id SERIAL PRIMARY KEY,
            task VARCHAR(255),
            deadline DATE NOT NULL,
            username VARCHAR(255),
            FOREIGN KEY (username) REFERENCES users(username)
        );
        """))
except Exception as e:
    print(f"Error creating tables: {e}")
    raise

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # This allows all headers
)
class User(BaseModel):
    username: str
    password: str 

class Task(BaseModel):
    task: str
    deadline: date 
    username: str
 

@app.get("/")
async def get():
    return {"message":"it works?"}

@app.post("/login/")
async def user_login(user: User):  
    try:
        with engine.begin() as conn:
            db = conn.execute(text("""
            SELECT * FROM users
            WHERE username =:username AND password = :password;
            """), {"username":user.username, "password":user.password})
            if not db.mappings().all():
                return {"status":"Invalid credentials!"}
            return {"status":"User logged in!"}
    except Exception as e:
        print(e)
        return {"status": "Login error!"}



@app.post("/create_user/")
async def create_user(user: User):
    try:
        with engine.begin() as conn:
            # Check if user exists
            db = conn.execute(
                text("""
                SELECT * FROM users
                WHERE username = :username;
                """),
                {"username": user.username}
            )
            
            if db.mappings().all():
                return {"status": "User already exists!"}
            
            # Create user
            conn.execute(
                text("""
                INSERT INTO users (username, password)
                VALUES (:username, :password);
                """),
                {"username": user.username, "password": user.password}
            )
            return {"status": "User created successfully!"}
    except Exception as e:
        print(e)
        return {"status": "Creation error!"}
   
   
@app.post("/create_task/")
async def create_task(task: Task):
    try:
        with engine.begin() as conn:
            # Check if user exists
            db = conn.execute(
                text("""
                SELECT * FROM users
                WHERE username = :username;
                """),
                {"username": task.username}
            )
            
            if not db.mappings().all():
                return {"status": "User does not exist!"}
            
            # Create task
            conn.execute(
                text("""
                INSERT INTO tasks (task, deadline, username)
                VALUES (:task, :deadline, :username);
                """),
                {"task": task.task, "deadline": task.deadline, "username": task.username}
            )
            return {"status": "Task created successfully!"}
    except Exception as e:
        print(e)
        return {"status": "Task creation error!"}
    

@app.get("/get_tasks/")
async def get_tasks(name: str):
    try:
        with engine.begin() as conn:
            db = conn.execute(
                text("""
                SELECT task, deadline FROM tasks
                WHERE username = :username;
                """),
                {"username": name}
            )
            
            tasks = db.mappings().all()
            if not tasks:
                return {"status": "No tasks found for the user!"}
            
            return {"tasks": [{"task": t["task"], "deadline": t["deadline"]} for t in tasks]}
    except Exception as e:
        print(e)
        return {"status": "Error fetching tasks!"}