from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv
from database import get_connection, test_connection


## pip install these into system
#pip install mysql-connector-python python-dotenv
#pip install fastapi
#pip install uvicorn
load_dotenv()

app = FastAPI()
 
@app.get("/")
def root():
    return {"Running API"}

#checks if we can connect to database
@app.get("/db-check")
def db_check():
    if test_connection():
        return {"database_connection": "successful"}
    else:
        return {"database_connection": "failed"}