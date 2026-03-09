from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv
from database import get_connection, test_connection
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from fastapi import HTTPException



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

class Employee(BaseModel):
    FullName: str
    Email: str

class EquipmentInfo(BaseModel):
    EquipmentName: str
    Sensitive: int
    NumofEquip: int

class RoomInfo(BaseModel):
    BuildingNumber: str
    RoomNumber: str
    FloorNumber: int
    RoomUseCode: str
    SpaceCode: str
    FurnitureCode: str
    SquareFeet: float
    Notes: str
    DepartmentName: str
    Assignedppl: List[Employee] = []
    Equipment: List[EquipmentInfo] = []



@app.get("/")
def root():
    return {"Running API"}

def validatePermission(required_permission: int, userId: int, affiliation: Dict[str, Any]) -> bool:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT u.Role_ID AS RoleID, d.DeptID AS DeptID, d.College AS College
            FROM Users u
            LEFT JOIN Employees e ON u.Email = e.Email
            LEFT JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
            WHERE u.UserID = %s
            LIMIT 1
        """
        cur.execute(query, (userId,))
        user = cur.fetchone()
        if not user:
            return False
        user_perm = user["RoleID"]
        if user_perm > required_permission:
            return False
        if not affiliation:
            return True
        
        user_dept = user["DeptID"]
        user_college = user["College"]

        if "department" in affiliation:
            dept_required = affiliation["department"]
            if isinstance(dept_required, list):
                if user_dept not in dept_required:
                    return False
            else:
                if user_dept != dept_required:
                    return False
                
        if "college" in affiliation:
            if user_college != affiliation["college"]:
                return False
        
        return True
    finally:
        cur.close()
        conn.close()

        



@app.get("/getRoomInfo", response_model= RoomInfo)
def getRoomInfo(buildingnumber: str, roomnumber: str):
    """
    Returns full information about a single room. Specific information includes:
    ● all individual attributes in the Rooms table of your database, including (even though this
    might be redundant) the bounding box information, purpose of the room, and the room's
    square footage.r
    ● The name of the department that controls the room.
    ● List of people assigned to the room. For each person, retrieve:
    ○ Their full name
    ○ Their email address
    ○ Their rank and/or position (e.g., Assistant Professor or Financial Analyst)
    ● List of equipment assigned to the room. For each type of equipment, retrieve:
    ○ its name (e.g., "computer workstation")
    ○ whether this type of equipment is considered sensitive
    ○ count of the number of pieces of equipment of this type in the room
    """
    RoomInfoQuery = """
    SELECT r.*, d.DepartmentName
    FROM Rooms r
    JOIN RoomsAreAssignedToDepts_Subdiv raatd ON r.BuildingNumber = raatd.BuildingNumber
     AND r.RoomNumber =raatd.RoomNumber
    JOIN Departments_Subdivisions d ON raatd.DeptID = d.DeptID
    WHERE r.BuildingNumber = %s AND r.RoomNumber = %s
    """
    RoomEmployeeQuery = """
    SELECT e.FullName, e.Email
    FROM Employees e
    JOIN EmployeesAssignedToRooms eatr
     ON e.EmpID = eatr.EmpID
    WHERE eatr.BuildingNumber = %s AND eatr.RoomNumber = %s
    """
    RoomEquipQuery = """
    SELECT eq.EType, eq.IsSensitive, req.Quantity
    FROM Equipment eq
    JOIN RoomsAreEquippedWithEquipment req 
     ON eq.EId = req.EId
    WHERE req.BuildingNumber = %s AND req.RoomNumber = %s
    """

    conn = get_connection()
    try:
        #get room information and what department teaches in that room
        cur = conn.cursor(dictionary=True)
        cur.execute(RoomInfoQuery, (buildingnumber, roomnumber))
        room = cur.fetchone()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        #get a list of all employees assigned to that room
        cur.execute(RoomEmployeeQuery, (buildingnumber, roomnumber))
        employees = cur.fetchall()

        #get a list of all equipment in that room
        cur.execute(RoomEquipQuery, (buildingnumber, roomnumber))
        equipment = cur.fetchall()

        return {
            "BuildingNumber": room["BuildingNumber"],
            "RoomNumber" : room["RoomNumber"],
            "FloorNumber" : room["FloorNumber"],
            "RoomUseCode" : room["RoomUseCode"],
            "SpaceCode" : room["SpaceCode"],
            "FurnitureCode": room["FurnitureCode"],
            "SquareFeet" : room["SquareFeet"],
            "Notes" : room["Notes"],
            "DepartmentName": room["DepartmentName"],
            "Assignedppl" : employees,
            "Equipment" : equipment
        }
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

@app.get("/findRoom", response_model=list[SelectedRoom])
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

@app.get("/getRooms", response_model=list[Room])
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



@app.get("/getFloorplans", response_model=list[FloorPlan])
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
    