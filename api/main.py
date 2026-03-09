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

class Room(BaseModel):
    BuildingNumber: str
    RoomNumber: str
    TopLeftX: int
    TopLeftY: int
    BottomRightX: int
    BottomRightY: int
    DepartmentName: str

class SelectedRoom(BaseModel):
    BuildingNumber: str
    RoomNumber: str

class RoomInfo(BaseModel):
    BuildingNumber: str
    RoomNumber: str
    FloorNumber: int
    RoomUseCode: int
    SpaceCode: int
    FurnitureCode: int
    SquareFeet: float
    Notes: str



@app.get("/")
def root():
    return {"Running API"}

@app.get("/getRoomInfo{buildingnumber}", response_model= list[RoomInfo])

@app.get("/findroom", response_model=list[SelectedRoom])
def find_room(buildingnumber: str, floornumber: int, x: int, y: int):
    """
    Find the selected room determined by the specified x and y coordinates. The returned room is usually the room within the bounding box,
    but if x and y are one the border between bounding boxes, return the room with the smallest area
    """

    query = """
    WITH getRooms AS (
  SELECT
    r.BuildingNumber AS BuildingNumber,
    r.RoomNumber AS RoomNumber,
    rc.TopLeftX AS TopLeftX,
    rc.TopLeftY AS TopLeftY,
    rc.BottomRightX AS BottomRightX,
    rc.BottomRightY AS BottomRightY
  FROM Rooms r
  JOIN RoomCoordinates rc
    ON r.BuildingNumber = rc.BuildingNumber
   AND r.RoomNumber = rc.RoomNumber
  WHERE r.BuildingNumber = %s
    AND r.FloorNumber = %s
    AND %s BETWEEN rc.TopLeftX AND rc.BottomRightX
    AND %s BETWEEN rc.TopLeftY AND rc.BottomRightY
),
calcArea AS (
  SELECT
    *,
    (ABS(BottomRightX - TopLeftX) * ABS(BottomRightY - TopLeftY)) AS RoomArea
  FROM getRooms
)
SELECT BuildingNumber, RoomNumber
FROM calcArea
ORDER BY RoomArea ASC
LIMIT 1;
    """
    conn = get_connection()
    try:
        curr = conn.cursor(dictionary=True)
        curr.execute(query, (buildingnumber, floornumber, x, y))
        rows = curr.fetchall()
        return rows
    
    finally:
        curr.close()
        conn.close()

@app.get("/rooms", response_model=list[Room])
def get_rooms(buildingnumber: str, floornumber: int):
    """
    Input building number and floor number to get all available rooms
    for that building on that floor
    """
    query = """
SELECT
  r.BuildingNumber,
  r.RoomNumber,
  rc.TopLeftX,
  rc.TopLeftY,
  rc.BottomRightX,
  rc.BottomRightY,
  d.DepartmentName
FROM Rooms r
JOIN RoomCoordinates rc
  ON r.BuildingNumber = rc.BuildingNumber
 AND r.RoomNumber = rc.RoomNumber
JOIN RoomsAreAssignedToDepts_Subdiv ra
  ON r.BuildingNumber = ra.BuildingNumber
 AND r.RoomNumber = ra.RoomNumber
JOIN Departments_Subdivisions d
  ON ra.DeptID = d.DeptID
  WHERE r.BuildingNumber = %s
   AND r.FloorNumber = %s
    """
    conn = get_connection()
    try:
        curr = conn.cursor(dictionary=True)
        curr.execute(query, (buildingnumber, floornumber))
        rows = curr.fetchall()
        return rows
    
    finally:
        curr.close()
        conn.close()



@app.get("/floorplans", response_model=list[FloorPlan])
def get_floor_plans():
    """
    Gets all avaialable floor plans
    """
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
    