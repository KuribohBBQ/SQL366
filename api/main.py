from fastapi import FastAPI
import mysql.connector
import os
import sqlalchemy
from dotenv import load_dotenv
from database import get_connection, test_connection
from pydantic import BaseModel, Field


## pip install these into system
#pip install mysql-connector-python python-dotenv
#pip install fastapi
#pip install uvicorn
load_dotenv()

app = FastAPI()
 
#format for getting list of floor plans
class FloorPlan(BaseModel):
    URI: str
    BuildingName: str
    BuildingNumber: str
    FloorNumber: int

@app.get("/")
def root():
    return {"Running API"}

@app.get("/floorplans", response_model=list[FloorPlan])
def get_floor_plans():
    query = """
    SELECT
        FileName AS URI,
        Buildings.Name AS BuildingName,
        FloorPlans.BuildingNumber AS BuildingNumber,
        FloorNumber AS FloorNumber
    FROM FloorPlans
    JOIN Buildings ON FloorPlans.BuildingNumber = Buildings.BuildingNumber
    """

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query)
        rows = cur.fetchall()
        return rows
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()


#checks if we can connect to database
@app.get("/db-check")
def db_check():
    if test_connection():
        return {"database_connection": "successful"}
    else:
        return {"database_connection": "failed"}
    