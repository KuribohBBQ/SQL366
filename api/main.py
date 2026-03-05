from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv


## pip install these into system
#pip install mysql-connector-python python-dotenv
#pip install fastapi
#pip install uvicorn
load_dotenv()

app = FastAPI()

#checks if we can connect to database
@app.get("/db-check")
def db_check():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )

        if conn.is_connected():
            conn.close()
            return {"database_connection": "successful"}

    except mysql.connector.Error as err:
        return {
            "database_connection": "failed",
            "error": str(err)
        }