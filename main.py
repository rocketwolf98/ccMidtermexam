from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd 
import numpy as np
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
    conn= engine.connect()
except Exception as e:
    print(f"Error connecting to database {e}")
    raise

ins = inspect(engine)

generate_users = conn.execute(text("""
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

conn.commit()
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
    db = conn.execute(text("""
    SELECT * FROM users
    WHERE username =:username AND password = :password;
    """), {"username":user.username, "password":user.password})
    if not db.mappings().all():
       return {"status":"User exists!"}
    else:
       return {"status":"User logged in!"}



@app.post("/create_user/")
async def create_user(user: User):
    db = conn.execute(
        text("""
        SELECT * FROM users
        WHERE username = :username;
        """),
        {"username": user.username}
    )
    
    if db.mappings().all():
        return {"status": "User already exists!"}
    
    try:
        conn.execute(
            text("""
            INSERT INTO users (username, password)
            VALUES (:username, :password);
            """),
            {"username": user.username, "password": user.password}
        )
        conn.commit()
        return {"status": "User created successfully!"}
    except Exception as e:
        print(e)
        return {"status": "Creation error!"}
   
   
@app.post("/create_task/")
async def create_task(task: Task):
    db = conn.execute(
        text("""
        SELECT * FROM users
        WHERE username = :username;
        """),
        {"username": task.username}
    )
    
    if not db.mappings().all():
        return {"status": "User does not exist!"}
    
    try:
        conn.execute(
            text("""
            INSERT INTO tasks (task, deadline, username)
            VALUES (:task, :deadline, :username);
            """),
            {"task": task.task, "deadline": task.deadline, "username": task.username}
        )
        conn.commit()
        return {"status": "Task created successfully!"}
    except Exception as e:
        print(e)
        return {"status": "Task creation error!"}
    

@app.get("/get_tasks/")
async def get_tasks(name: str):
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