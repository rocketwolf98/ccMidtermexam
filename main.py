from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd 
import numpy as np

from sqlalchemy import create_engine, inspect
from sqlalchemy import text

import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL= os.getenv("DATABASE_URL") 
engine = create_engine(DATABASE_URL,  client_encoding='utf8')

conn= engine.connect()
ins = inspect(engine)

generate_users = conn.execute(text("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL);
    
CREATE TABLE IF NOT EXISTS tasks(
    task VARCHAR(255),
    deadline DATE NOT NULL,
    username VARCHAR(255),
    FOREIGN KEY (username) REFERENCES users(username);
    ));
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
    deadline: str 
    username: str
 

@app.get("/")
async def get():
    return {"message":"it works?"}

@app.post("/login/")
async def user_login(user: User):  
    db = conn.execute("""
    SELECT * FROM users
    WHERE username =:username;
    """, {"username":user.username})
    if not db.mappings().all():
       return {"status":"User exists!"}
    else:
       return {"status":"User logged in!"}



@app.post("/create_user/")
async def create_user(user: User):
    db = conn.execute("""
    SELECT * FROM users
    WHERE username =:username;
                     """, {"username":user.username})
    if not db.mappings().all():
       return {"status":"User exists!"}
    
    try:
        conn.execute("""
        INSERT INTO users (username, password)
        VALUES (:username, :password);""",
        {"username": user.username, "password":user.password})
        conn.commit()
    except Exception as e:
        print(e)
        return {"status":"Creation error!"}
   
   
@app.post("/create_task/")
async def create_task(task: Task):
    db = conn.execute("""
    SELECT * FROM users
    WHERE username =:username;
                     """, {"username":task.username})
    if not db.mappings().all():
       return {"status":"User does not exist!"}
   
    try:
        conn.execute("""
        INSERT INTO tasks (task, deadline, username)
        VALUES (:task, :deadline, :username);""",
        {"task":task.task, "deadline": task.deadline, "username": task.username})
        conn.commit()
    except Exception as e:
        print(e)
        return {"status":"Creation error!"}
    

@app.get("/get_tasks/")
async def get_tasks(name: str):
    db = conn.execute("""
    SELECT * FROM tasks
    WHERE username = :username;
    """, username = tasks.username)
    if not db.mappings().all():
        return {"status":"User exists!"}
    else:
        tasks = db.mappings().all()
        return {"tasks":tasks}

    return {"tasks": [ ['laba','2','a'] , ['study','6','a'] , ['code','10','a']  ] }
