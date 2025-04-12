from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd 
import numpy as np

from sqlalchemy import create_engine, inspect
from sqlalchemy import text

import os
from dotenv import load_dotenv
load_dotenv()

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

generate_task = conn.execute(text("""
"""))
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
    user: str
 

@app.get("/")
async def get():
    return {"message":"it works?"}

@app.post("/login/")
async def user_login(User: User):  
    db = conn.execute("""
    SELECT * FROM users
    WHERE username =:username;
    """, username=user.username)
    if not db.mappings().all():
       return {"status":"User exists!"}
    else:
       return {"status":"User logged in!"}



@app.post("/create_user/")
async def create_user(User: User):
    db = conn.execute("""
    SELECT * FROM users
    WHERE username =:username;
                     """, username=user.username)
    if not db.mappings().all():
       return {"status":"User exists!"}
    
    try:
        conn.execute("""
        INSERT INTO users (username, password)
        VALUES (:username, :password);""",
        username= user.username, password= user.password)
        conn.commit()
    except Exception as e:
        print(e)
        return {"status":"Creation error!"}
   
   
@app.post("/create_task/")
async def create_task(Task: Task):
    db = conn.execute("""
    SELECT * FROM users
    WHERE username =:username;
                     """, username=task.username)
    if not db.mappings().all():
       return {"status":"User does not exist!"}
   
    try:
        conn.execute("""
        INSERT INTO tasks (task, deadline, username)
        VALUES (:task, :deadline, :username);""",
        task= tasks.task, deadline= tasks.deadline, username = tasks.username)
        conn.commit()
    except Exception as e:
        print(e)
        return {"status":"Creation error!"}
    

@app.get("/get_tasks/")
async def get_tasks(name: str):

    

    return {"tasks": [ ['laba','2','a'] , ['study','6','a'] , ['code','10','a']  ] }
