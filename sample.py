from sqlalchemy import create_engine, inspect
from sqlalchemy import text

import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL= os.getenv("DATABASE_URL") 
engine = create_engine(DATABASE_URL,  client_encoding='utf8')

connection = engine.connect()
asd = inspect(engine) 


print (asd.get_table_names())


result = connection.execute(
    text("""CREATE TABLE IF NOT EXISTS users ( id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);"""))


print( result )

# x = connection.execute(
#     text("""INSERT INTO users (username, password) VALUES ('reqw','reqw');
# ;"""))


q = connection.execute(
    text(""" SELECT * FROM users
    ;"""))

print(q.mappings().all())
print(q.fetchall())



connection.commit()