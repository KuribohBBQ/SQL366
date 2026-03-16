from fastapi import FastAPI, Query, Depends
import mysql.connector
import os
from dotenv import load_dotenv
from api.database import get_connection, test_connection
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
    EType: str
    IsSensitive: int
    Quantity: int

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

class EmployeeRoomShare(BaseModel):
    BuildingNumber: str
    RoomNumber: str
    EmployeeShareSquareFeet: float

class EmployeeWithRooms(BaseModel):
    FullName: str
    Email: str
    Rooms: List[EmployeeRoomShare] = []
    TotalSpaceSquareFeet: float

class EmployeeRoomDetail(BaseModel):
    BuildingNumber: str
    RoomNumber: str
    RoomType: str
    RoomSquareFeet: float
    EmployeeShareSquareFeet: float

class EmployeeInfoResponse(BaseModel):
    FullName: str
    DepartmentName: str
    Email: str
    TotalSpaceSquareFeet: float
    Rooms: List[EmployeeRoomDetail] = []

class EquipmentLocation(BaseModel):
    BuildingNumber: str
    RoomNumber: str
    Quantity: int

class EquipmentLocationsResponse(BaseModel):
    EType: str
    Locations: List[EquipmentLocation]

class SensitiveEquipmentGroup(BaseModel):
    EType: str
    TotalQuantity: int
    Locations: List[EquipmentLocation] = []

class SensitiveEquipmentByCollegeResponse(BaseModel):
    College: str
    RoomCount: int
    SensitiveEquipment: List[SensitiveEquipmentGroup] = []

class DeptListEnhancedRow(BaseModel):
    DeptID: int
    DepartmentName: str
    NumAssignedRooms: int
    NumRoomsWithDeptEmployees: int
    AssignedRoomsSquareFeet: float
    EmployeeAllocatedSquareFeet: float


class DeptListRow(BaseModel):
    DepartmentName: str
    MainOfficeLocation: Optional[str] = None
    DepartmentHead: Optional[str] = None
    DepartmentType: str


class AddEmployeeInput(BaseModel):
    FullName: str
    Email: str
    DeptID: int
    PositionTitle: Optional[str] = None


class RoomAssignmentInput(BaseModel):
    EmployeeEmail: str
    BuildingNumber: str
    RoomNumber: str


class DepartmentAssignmentInput(BaseModel):
    DeptID: int
    BuildingNumber: str
    RoomNumber: str


class EquipmentAssignmentInput(BaseModel):
    BuildingNumber: str
    RoomNumber: str
    EType: str
    NewCount: int


class EquipmentTypeInput(BaseModel):
    EType: str
    IsSensitive: bool = False
    EDescription: str = ""


SUCCESS_CODE = "SUCCESS"
ERR_UNAUTHORIZED = "ERR_UNAUTHORIZED"
ERR_DUPLICATE = "ERR_DUPLICATE"
ERR_FK_VIOLATION = "ERR_FK_VIOLATION"
ERR_TYPE_MISMATCH = "ERR_TYPE_MISMATCH"
ERR_LOGGING_FAILURE = "ERR_LOGGING_FAILURE"
ERR_NOT_FOUND = "ERR_NOT_FOUND"
    

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
        print("DEBUG user row:", user)
        if not user:
            return False
        user_perm = user["RoleID"]
        if user_perm > required_permission:
            return False
        if user_perm == 1:
            return True
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

        

def require_permission(required_permission: int, affiliation: Dict[str, Any] | None = None):
    affiliation = affiliation or {}

    def _dep(userId: int = Query(..., description="UserID performing the action")):
        if not validatePermission(required_permission, userId, affiliation):
            raise HTTPException(status_code=403, detail="Permission denied")
        return True

    return _dep


@app.get("/validatePermission", tags=["Part0"], summary="Validate Permission")
def validate_permission_endpoint(required_permission: int, userId: int, department: Optional[int] = None, college: Optional[str] = None):
    affiliation: Dict[str, Any] = {}
    if department is not None:
        affiliation["department"] = [department]
    if college:
        affiliation["college"] = college
    return {"allowed": validatePermission(required_permission, userId, affiliation)}


def _error_result(code: str, message: str = "") -> Dict[str, Any]:
    return {"ErrorCode": code, "Message": message}


def _room_affiliation(conn, building_number: str, room_number: str) -> Dict[str, Any]:
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT ra.DeptID, d.College
            FROM RoomsAreAssignedToDepts_Subdiv ra
            JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE ra.BuildingNumber = %s AND ra.RoomNumber = %s
            """,
            (building_number, room_number),
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    dept_ids = [int(r["DeptID"]) for r in rows if r.get("DeptID") is not None]
    colleges = sorted({str(r["College"]) for r in rows if r.get("College")})

    affiliation: Dict[str, Any] = {}
    if dept_ids:
        affiliation["department"] = dept_ids
    if len(colleges) == 1:
        affiliation["college"] = colleges[0]
    return affiliation


def _dept_affiliation(conn, dept_id: int) -> Dict[str, Any]:
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT DeptID, College
            FROM Departments_Subdivisions
            WHERE DeptID = %s
            LIMIT 1
            """,
            (dept_id,),
        )
        row = cur.fetchone()
    finally:
        cur.close()

    if not row:
        return {}
    return {"department": [int(row["DeptID"])], "college": row["College"]}


def _log_room_assignment_person(conn, user_id: int, building: str, room: str, emp_id: int, action: str) -> str:
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Logs (UserID, AssignOrDelete, BuildingNumber, RoomNumber, EmpID)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, action[:10], building, room, emp_id),
        )
        return SUCCESS_CODE
    except Exception:
        return ERR_LOGGING_FAILURE
    finally:
        cur.close()


def _log_equipment_assignment(conn, user_id: int, building: str, room: str, eid: int, after_count: int) -> str:
    action = "Delete" if after_count == 0 else "Assign"
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Logs (UserID, AssignOrDelete, BuildingNumber, RoomNumber, EId, Quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, action, building, room, eid, after_count),
        )
        return SUCCESS_CODE
    except Exception:
        return ERR_LOGGING_FAILURE
    finally:
        cur.close()


def _log_room_dept_change(conn, user_id: int, building: str, room: str, to_dept: Optional[int]) -> str:
    action = "Assign" if to_dept is not None else "Delete"
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Logs (UserID, AssignOrDelete, BuildingNumber, RoomNumber, DeptID)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, action, building, room, to_dept),
        )
        return SUCCESS_CODE
    except Exception:
        return ERR_LOGGING_FAILURE
    finally:
        cur.close()

@app.get("/getRoomInfo", tags=["Rooms"], summary="Get Room Information", response_model= RoomInfo, dependencies=[Depends(require_permission(5))])
def getRoomInfo(buildingnumber: str, roomnumber: str):
    """
    Given a room and building number, it returns all information about that room.
    Specific information would include:
      all attribute of the room,
      name of assigned department,
      list of people assigned to the room, 
      and information for all those people,
      types of equipment, their types, and quantities.
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

@app.get("/findRoom", tags=["Rooms"], response_model=list[SelectedRoom], dependencies=[Depends(require_permission(5))])
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

@app.get("/getRooms", tags=["Rooms"], response_model=list[Room], dependencies=[Depends(require_permission(5))])
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



@app.get("/getFloorplans", tags=["Floorplans"], response_model=list[FloorPlan], dependencies=[Depends(require_permission(5))])
def get_floor_plans():
    """
    Gets all available floor plans
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
@app.get("/db-check", dependencies=[Depends(require_permission(3))])
def db_check():
    if test_connection():
        return {"database_connection": "successful"}
    else:
        return {"database_connection": "failed"}
    

#List of Employees (getEmployees) 
@app.get("/getEmployees", tags=["Employees"], summary="Get All Employees", response_model=List[EmployeeWithRooms], dependencies=[Depends(require_permission(5))])
def getEmployees(college: str, department: str):
    """
    Given a College name and Department/Subdivision name, returns employees in that dept,
    including contact info, their rooms, and computed total space in their purview.
    """
    employee_query = """
        SELECT
            e.EmpID,
            e.FullName,
            e.Email
        FROM Employees e
        JOIN Departments_Subdivisions d on e.DeptID = d.DeptID
        WHERE d.College = %s
            AND d.DepartmentName = %s
        ORDER BY e.FullName
    """

    rooms_query = """
        WITH occupants AS (
            SELECT
                eatr.BuildingNumber,
                eatr.RoomNumber,
                COUNT(*) AS occupant_count
            FROM EmployeesAssignedToRooms eatr
            GROUP BY eatr.BuildingNumber, eatr.RoomNumber
        )
        SELECT
            e.EmpID,
            r.BuildingNumber,
            r.RoomNumber,
            r.SquareFeet,
            o.occupant_count,
            CASE
                WHEN o.occupant_count = 1 THEN r.SquareFeet
                ELSE r.SquareFeet / o.occupant_count
            END AS employee_share
        FROM Employees e
        JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
        JOIN EmployeesAssignedToRooms eatr ON e.EmpID = eatr.EmpID
        JOIN Rooms r
          ON r.BuildingNumber = eatr.BuildingNumber
         AND r.RoomNumber = eatr.RoomNumber
        JOIN occupants o
          ON o.BuildingNumber = eatr.BuildingNumber
         AND o.RoomNumber = eatr.RoomNumber
        WHERE d.College = %s
          AND d.DepartmentName = %s
        ORDER BY e.EmpID, r.BuildingNumber, r.RoomNumber
    """

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute(employee_query, (college, department))
        employees = cur.fetchall()

        if not employees:

            return []

        emp_map = {}
        for e in employees:
            emp_map[e["EmpID"]] = {
                "FullName": e["FullName"],
                "Email": e["Email"],
                "Rooms": [],
                "TotalSpaceSquareFeet": 0.0,
            }

        cur.execute(rooms_query, (college, department))
        room_rows = cur.fetchall()

        for row in room_rows:
            emp_id = row["EmpID"]
            if emp_id not in emp_map:
                continue

            share = float(row["employee_share"]) if row["employee_share"] is not None else 0.0
            emp_map[emp_id]["Rooms"].append({
                "BuildingNumber": row["BuildingNumber"],
                "RoomNumber": row["RoomNumber"],
                "EmployeeShareSquareFeet": share,
            })
            emp_map[emp_id]["TotalSpaceSquareFeet"] += share

        # Return as list in the same order as employee_query
        return [emp_map[e["EmpID"]] for e in employees]

    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()


@app.get("/getEmployeeInfo", tags=["Employees"], summary= "Get Employee Information", response_model=EmployeeInfoResponse, dependencies=[Depends(require_permission(5))])
def getEmployeeInfo(
    email: Optional[str] = None,
    name: Optional[str] = None,
    department: Optional[str] = None,
):
    """
    Input email or name and department of employee you are looking for
    """
    if not email and not (name and department):
        raise HTTPException(
            status_code=422,
            detail="Provide either email=... OR name...&department=..."
        )
    
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)

        if email:
            emp_query = """
                SELECT 
                    e.EmpID,
                    e.FullName,
                    e.Email,
                    d.DepartmentName
                FROM Employees e
                JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
                WHERE e.Email = %s
                LIMIT 1
            """

            cur.execute(emp_query, (email,))
        else:
            emp_query = """
                SELECT
                    e.EmpID,
                    e.FullName,
                    e.Email,
                    d.DepartmentName
                FROM Employees e
                JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
                WHERE e.FullName = %s
                  AND d.DepartmentName = %s
                LIMIT 1
            """
            cur.execute(emp_query, (name, department))
        emp = cur.fetchone()
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        emp_id = emp["EmpID"]

        rooms_query = """
            WITH occupants AS (
                SELECT
                    eatr.BuildingNumber,
                    eatr.RoomNumber,
                    COUNT(*) AS occupant_count
                FROM EmployeesAssignedToRooms eatr
                GROUP By eatr.BuildingNumber, eatr.RoomNumber
            )
            SELECT
                r.BuildingNumber,
                r.RoomNumber,
                r.RoomUseCode AS RoomType,
                r.SquareFeet AS RoomSquareFeet,
                o.occupant_count
            FROM EmployeesAssignedToRooms eatr
            JOIN Rooms r
              ON r.BuildingNumber = eatr.BuildingNumber
             AND r.RoomNumber = eatr.RoomNumber
            JOIN occupants o
              ON o.BuildingNumber = eatr.BuildingNumber
             AND o.RoomNumber = eatr.RoomNumber
            WHERE eatr.EmpID = %s
            ORDER BY r.BuildingNumber, r.RoomNumber
        """

        cur.execute(rooms_query, (emp_id,))
        rooms_row = cur.fetchall()

        rooms_out = []
        total_share = 0.0

        for rr in rooms_row:
            room_sqft = float(rr["RoomSquareFeet"]) if rr["RoomSquareFeet"] is not None else 0.0
            occ = int(rr["occupant_count"]) if rr["occupant_count"] is not None else 1
            share = compute_employee_share(room_sqft, occ)
            total_share += share

            rooms_out.append({
                "BuildingNumber": rr["BuildingNumber"],
                "RoomNumber": rr["RoomNumber"],
                "RoomType": rr["RoomType"],
                "RoomSquareFeet": room_sqft,
                "EmployeeShareSquareFeet": share,
            })
        
        return {
            "FullName": emp["FullName"],
            "DepartmentName": emp["DepartmentName"],
            "Email": emp["Email"],
            "TotalSpaceSquareFeet": total_share,
            "Rooms": rooms_out,
        }
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

    

# helper functions
def compute_employee_share(room_sqft: float, occupant_count: int) -> float:
    if occupant_count <= 1:
        return float(room_sqft)
    return float(room_sqft) / float(occupant_count)
    

@app.get("/getEquipmentLocations", tags=["Equipment"], summary=" Get Equipment Locations", response_model=EquipmentLocationsResponse, dependencies=[Depends(require_permission(5))])
def getEquipmentLocation(etype: str):
    """
    Input equipment type to get all rooms
    that have that equipment type
    """
    query ="""
            SELECT 
                req.BuildingNumber,
                req.RoomNumber,
                SUM(req.Quantity) AS Quantity
            FROM Equipment eq
            JOIN RoomsAreEquippedWithEquipment req
              ON eq.EId = req.EId
            WHERE eq.EType LIKE %s
            GROUP BY req.BuildingNumber, req.RoomNumber
            ORDER BY req.BuildingNumber, req.RoomNumber
    """
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, (f"%{etype}%",))
        rows = cur.fetchall()
        for r in rows:
            r["Quantity"] = int(r["Quantity"])
        return {
            "EType": etype,
            "Locations": rows
        }
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

@app.get("/getSensitiveEquipmentLocations", tags=["Equipment"], summary="Get Sensitive Equipment Report by College", response_model=SensitiveEquipmentByCollegeResponse, dependencies=[Depends(require_permission(5))])
def getSensitiveEquipmentLocations(college: str):
    """
        Input a college and all sensitive equipment that belongs to that college will be returned.
    """

    query = """
        SELECT
            d.College AS College,
            eq.EType AS EType,
            req.BuildingNumber AS BuildingNumber,
            req.RoomNumber AS RoomNumber,
            SUM(req.Quantity) AS Quantity
        FROM RoomsAreEquippedWithEquipment req
        JOIN Equipment eq
          ON eq.EId = req.EId
        JOIN RoomsAreAssignedToDepts_Subdiv ra
          ON ra.BuildingNumber = req.BuildingNumber
         AND ra.RoomNumber = req.RoomNumber
        JOIN Departments_Subdivisions d
          ON d.DeptID = ra.DeptID
        WHERE eq.IsSensitive = 1
          AND d.College = %s
        GROUP BY d.College, eq.EType, req.BuildingNumber, req.RoomNumber
        ORDER BY eq.EType, req.BuildingNumber, req.RoomNumber;
    """

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, (college,))
        rows = cur.fetchall()

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            etype = r["EType"]
            groups.setdefault(etype, []).append({
                "BuildingNumber": r["BuildingNumber"],
                "RoomNumber": r["RoomNumber"],
                "Quantity": int(r["Quantity"]),
            })

        sensitive_equipment = []
        for etype in sorted(groups.keys()):
            locs = groups[etype]
            total = sum(loc["Quantity"] for loc in locs)
            sensitive_equipment.append({"EType": etype, "TotalQuantity": total, "Locations": locs})

        room_set = {(loc["BuildingNumber"], loc["RoomNumber"]) for locs in groups.values() for loc in locs}
        return {
            "College": college,
            "RoomCount": int(len(room_set)),
            "SensitiveEquipment": sensitive_equipment,
        }
    finally:
        cur.close()
        conn.close()


@app.get("/getDeptList", tags=["Rooms"], summary="Get Department List", response_model=List[DeptListRow], dependencies=[Depends(require_permission(5))])
def getDeptList(college: str):
    """
    Basic department list for a college.
    """
    query = """
        SELECT
            d.DepartmentName,
            MIN(CONCAT(ra.BuildingNumber, '-', ra.RoomNumber)) AS MainOfficeLocation
        FROM Departments_Subdivisions d
        LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra
          ON ra.DeptID = d.DeptID
        WHERE d.College = %s
        GROUP BY d.DeptID, d.DepartmentName
        ORDER BY d.DepartmentName
    """
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, (college,))
        rows = cur.fetchall()

        output = []
        for row in rows:
            output.append(
                {
                    "DepartmentName": row["DepartmentName"],
                    "MainOfficeLocation": row["MainOfficeLocation"],
                    "DepartmentHead": None,
                    "DepartmentType": "Academic" if "science" in row["DepartmentName"].lower() else "Subdivision",
                }
            )
        return output
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

@app.get("/getDeptListEnhanced", tags=["Rooms"], summary="Get Department Information", response_model=List[DeptListEnhancedRow], dependencies=[Depends(require_permission(5))])
def getDeptListEnhanced(college: str):
    """
        Input a college and returns all information about departments and their number of assigned rooms, square footage of assigned rooms, 
        rooms where at least one employee of that department is assigned, and square footage assigned to department employees.
    """

    dept_query = """
        SELECT DeptID, DepartmentName
        FROM Departments_Subdivisions
        WHERE College = %s
        ORDER BY DepartmentName;
    """

    deptrm_query = """
        SELECT
            ra.DeptID,
          COUNT(DISTINCT CONCAT(ra.BuildingNumber,'|',ra.RoomNumber)) AS NumAssignedRooms,
          COALESCE(SUM(r.SquareFeet), 0) AS AssignedRoomsSquareFeet
        FROM RoomsAreAssignedToDepts_Subdiv ra
        JOIN Rooms r
          ON r.BuildingNumber = ra.BuildingNumber
         AND r.RoomNumber = ra.RoomNumber
        JOIN Departments_Subdivisions d
          ON d.DeptID = ra.DeptID
        WHERE d.College = %s
        GROUP BY ra.DeptID;
    """

    rmtoemp_query = """
        SELECT
            e.DeptID,
            COUNT(DISTINCT CONCAT(eatr.BuildingNumber,'|',eatr.RoomNumber)) AS NumRoomsWithDeptEmployees
        FROM Employees e
        JOIN Departments_Subdivisions d
          ON d.DeptID = e.DeptID
        JOIN EmployeesAssignedToRooms eatr
          ON eatr.EmpID = e.EmpID
        WHERE d.College = %s
        GROUP BY e.DeptID;
    """

    sqfttoemp_query = """
        WITH occupants AS (
            SELECT
            BuildingNumber,
            RoomNumber,
            COUNT(*) AS occupant_count
          FROM EmployeesAssignedToRooms
          GROUP BY BuildingNumber, RoomNumber
        )
        SELECT
          e.DeptID,
          COALESCE(SUM(
            CASE
              WHEN o.occupant_count <= 1 THEN r.SquareFeet
              ELSE r.SquareFeet / o.occupant_count
            END
         ), 0) AS EmployeeAllocatedSquareFeet
        FROM Employees e
        JOIN Departments_Subdivisions d
          ON d.DeptID = e.DeptID
        JOIN EmployeesAssignedToRooms eatr
          ON eatr.EmpID = e.EmpID
        JOIN Rooms r
          ON r.BuildingNumber = eatr.BuildingNumber
         AND r.RoomNumber = eatr.RoomNumber
        JOIN occupants o
          ON o.BuildingNumber = eatr.BuildingNumber
         AND o.RoomNumber = eatr.RoomNumber
        WHERE d.College = %s
        GROUP BY e.DeptID;
    """

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(dept_query, (college,))
        depts = cur.fetchall()

        if not depts:
            return []
        
        dept_map = {}
        for drow in depts:
            dept_id = drow["DeptID"]
            dept_map[dept_id] = {
                "DeptID": dept_id,
                "DepartmentName": drow["DepartmentName"],
                "NumAssignedRooms": 0,
                "NumRoomsWithDeptEmployees": 0,
                "AssignedRoomsSquareFeet": 0.0,
                "EmployeeAllocatedSquareFeet": 0.0,
            }

        cur.execute(deptrm_query, (college,))
        for r in cur.fetchall():
            dept_id = r["DeptID"]
            if dept_id in dept_map:
                dept_map[dept_id]["NumAssignedRooms"] = int(r["NumAssignedRooms"])
                dept_map[dept_id]["AssignedRoomsSquareFeet"] = float(r["AssignedRoomsSquareFeet"])

        cur.execute(rmtoemp_query, (college,))
        for r in cur.fetchall():
            dept_id = r["DeptID"]
            if dept_id in dept_map:
                dept_map[dept_id]["NumRoomsWithDeptEmployees"] = int(r["NumRoomsWithDeptEmployees"])

        cur.execute(sqfttoemp_query, (college,))
        for r in cur.fetchall():
            dept_id = r["DeptID"]
            if dept_id in dept_map:
                dept_map[dept_id]["EmployeeAllocatedSquareFeet"] = float(r["EmployeeAllocatedSquareFeet"])

        return [dept_map[drow["DeptID"]] for drow in depts]
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()


@app.post("/addEmployee", tags=["Part2"], summary="Add Employee")
def addEmployee(userId: int, payload: AddEmployeeInput):
    conn = get_connection()
    try:
        affiliation = _dept_affiliation(conn, payload.DeptID)
        if not validatePermission(3, userId, affiliation):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Employees (Email, FullName, DeptID)
            VALUES (%s, %s, %s)
            """,
            (payload.Email, payload.FullName, payload.DeptID),
        )
        conn.commit()
        return _error_result(SUCCESS_CODE, "Employee added")
    except mysql.connector.IntegrityError as exc:
        conn.rollback()
        if exc.errno == 1062:
            return _error_result(ERR_DUPLICATE, "Duplicate employee/email")
        if exc.errno in (1451, 1452):
            return _error_result(ERR_FK_VIOLATION, "Invalid DeptID")
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    except Exception as exc:
        conn.rollback()
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    finally:
        conn.close()


@app.post("/assignRoom", tags=["Part2"], summary="Assign Employee to Room")
def assignRoom(userId: int, payload: RoomAssignmentInput):
    conn = get_connection()
    try:
        affiliation = _room_affiliation(conn, payload.BuildingNumber, payload.RoomNumber)
        if not validatePermission(3, userId, affiliation):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT EmpID FROM Employees WHERE Email = %s LIMIT 1", (payload.EmployeeEmail,))
        emp = cur.fetchone()
        if not emp:
            return _error_result(ERR_NOT_FOUND, "Employee not found")

        cur.execute(
            """
            SELECT 1
            FROM EmployeesAssignedToRooms
            WHERE EmpID = %s AND BuildingNumber = %s AND RoomNumber = %s
            LIMIT 1
            """,
            (emp["EmpID"], payload.BuildingNumber, payload.RoomNumber),
        )
        if cur.fetchone():
            return _error_result(ERR_DUPLICATE, "Assignment already exists")

        if _log_room_assignment_person(
            conn, userId, payload.BuildingNumber, payload.RoomNumber, int(emp["EmpID"]), "Assign"
        ) != SUCCESS_CODE:
            conn.rollback()
            return _error_result(ERR_LOGGING_FAILURE, "Could not create log")

        cur2 = conn.cursor()
        cur2.execute(
            """
            INSERT INTO EmployeesAssignedToRooms (EmpID, RoomNumber, BuildingNumber)
            VALUES (%s, %s, %s)
            """,
            (emp["EmpID"], payload.RoomNumber, payload.BuildingNumber),
        )
        cur2.close()

        conn.commit()
        return _error_result(SUCCESS_CODE, "Assigned")
    except Exception as exc:
        conn.rollback()
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    finally:
        conn.close()


@app.post("/removeRoomAssignment", tags=["Part2"], summary="Remove Employee Room Assignment")
def removeRoomAssignment(userId: int, payload: RoomAssignmentInput):
    conn = get_connection()
    try:
        affiliation = _room_affiliation(conn, payload.BuildingNumber, payload.RoomNumber)
        if not validatePermission(3, userId, affiliation):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT EmpID FROM Employees WHERE Email = %s LIMIT 1", (payload.EmployeeEmail,))
        emp = cur.fetchone()
        if not emp:
            return _error_result(ERR_NOT_FOUND, "Employee not found")

        cur.execute(
            """
            SELECT 1
            FROM EmployeesAssignedToRooms
            WHERE EmpID = %s AND BuildingNumber = %s AND RoomNumber = %s
            LIMIT 1
            """,
            (emp["EmpID"], payload.BuildingNumber, payload.RoomNumber),
        )
        if not cur.fetchone():
            return _error_result(ERR_NOT_FOUND, "Assignment not found")

        if _log_room_assignment_person(
            conn, userId, payload.BuildingNumber, payload.RoomNumber, int(emp["EmpID"]), "Delete"
        ) != SUCCESS_CODE:
            conn.rollback()
            return _error_result(ERR_LOGGING_FAILURE, "Could not create log")

        cur2 = conn.cursor()
        cur2.execute(
            """
            DELETE FROM EmployeesAssignedToRooms
            WHERE EmpID = %s AND BuildingNumber = %s AND RoomNumber = %s
            """,
            (emp["EmpID"], payload.BuildingNumber, payload.RoomNumber),
        )
        cur2.close()

        conn.commit()
        return _error_result(SUCCESS_CODE, "Removed")
    except Exception as exc:
        conn.rollback()
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    finally:
        conn.close()


@app.post("/departmentAssignment", tags=["Part2"], summary="Assign Room to Department")
def departmentAssignment(userId: int, payload: DepartmentAssignmentInput):
    conn = get_connection()
    try:
        affiliation = _dept_affiliation(conn, payload.DeptID)
        if not validatePermission(3, userId, affiliation):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")

        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT DeptID
            FROM RoomsAreAssignedToDepts_Subdiv
            WHERE BuildingNumber = %s AND RoomNumber = %s
            ORDER BY DeptID
            """,
            (payload.BuildingNumber, payload.RoomNumber),
        )
        old_rows = cur.fetchall()
        old_dept = int(old_rows[0]["DeptID"]) if old_rows else None

        if _log_room_dept_change(conn, userId, payload.BuildingNumber, payload.RoomNumber, payload.DeptID) != SUCCESS_CODE:
            conn.rollback()
            return _error_result(ERR_LOGGING_FAILURE, "Could not create log")

        cur2 = conn.cursor()
        cur2.execute(
            """
            DELETE FROM RoomsAreAssignedToDepts_Subdiv
            WHERE BuildingNumber = %s AND RoomNumber = %s
            """,
            (payload.BuildingNumber, payload.RoomNumber),
        )
        cur2.execute(
            """
            INSERT INTO RoomsAreAssignedToDepts_Subdiv (BuildingNumber, RoomNumber, DeptID)
            VALUES (%s, %s, %s)
            """,
            (payload.BuildingNumber, payload.RoomNumber, payload.DeptID),
        )
        cur2.close()

        conn.commit()
        return _error_result(SUCCESS_CODE, f"Changed from {old_dept} to {payload.DeptID}")
    except mysql.connector.IntegrityError as exc:
        conn.rollback()
        if exc.errno in (1451, 1452):
            return _error_result(ERR_FK_VIOLATION, "Invalid room or department")
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    except Exception as exc:
        conn.rollback()
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    finally:
        conn.close()


@app.post("/assignEquipment", tags=["Part2"], summary="Assign Equipment Count to Room")
def assignEquipment(userId: int, payload: EquipmentAssignmentInput):
    conn = get_connection()
    try:
        affiliation = _room_affiliation(conn, payload.BuildingNumber, payload.RoomNumber)
        if not validatePermission(3, userId, affiliation):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")
        if payload.NewCount < 0:
            return _error_result(ERR_TYPE_MISMATCH, "NewCount must be >= 0")

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT EId FROM Equipment WHERE EType = %s LIMIT 1", (payload.EType,))
        eq = cur.fetchone()
        if not eq:
            return _error_result(ERR_NOT_FOUND, "Equipment type not found")
        eid = int(eq["EId"])

        cur.execute(
            """
            SELECT Quantity
            FROM RoomsAreEquippedWithEquipment
            WHERE BuildingNumber = %s AND RoomNumber = %s AND EId = %s
            LIMIT 1
            """,
            (payload.BuildingNumber, payload.RoomNumber, eid),
        )
        existing = cur.fetchone()
        before_count = int(existing["Quantity"]) if existing else 0

        if _log_equipment_assignment(conn, userId, payload.BuildingNumber, payload.RoomNumber, eid, payload.NewCount) != SUCCESS_CODE:
            conn.rollback()
            return _error_result(ERR_LOGGING_FAILURE, "Could not create log")

        cur2 = conn.cursor()
        if payload.NewCount == 0:
            cur2.execute(
                """
                DELETE FROM RoomsAreEquippedWithEquipment
                WHERE BuildingNumber = %s AND RoomNumber = %s AND EId = %s
                """,
                (payload.BuildingNumber, payload.RoomNumber, eid),
            )
        elif before_count == 0:
            cur2.execute(
                """
                INSERT INTO RoomsAreEquippedWithEquipment (BuildingNumber, RoomNumber, EId, Quantity)
                VALUES (%s, %s, %s, %s)
                """,
                (payload.BuildingNumber, payload.RoomNumber, eid, payload.NewCount),
            )
        else:
            cur2.execute(
                """
                UPDATE RoomsAreEquippedWithEquipment
                SET Quantity = %s
                WHERE BuildingNumber = %s AND RoomNumber = %s AND EId = %s
                """,
                (payload.NewCount, payload.BuildingNumber, payload.RoomNumber, eid),
            )
        cur2.close()

        conn.commit()
        return _error_result(SUCCESS_CODE, f"Equipment count changed {before_count} -> {payload.NewCount}")
    except Exception as exc:
        conn.rollback()
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    finally:
        conn.close()


@app.post("/addEquipmentType", tags=["Part2"], summary="Add Equipment Type")
def addEquipmentType(userId: int, payload: EquipmentTypeInput):
    conn = get_connection()
    try:
        if not validatePermission(2, userId, {}):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Equipment (EType, EDescription, IsSensitive)
            VALUES (%s, %s, %s)
            """,
            (payload.EType, payload.EDescription, 1 if payload.IsSensitive else 0),
        )
        conn.commit()
        return _error_result(SUCCESS_CODE, "Equipment type added")
    except mysql.connector.IntegrityError as exc:
        conn.rollback()
        if exc.errno == 1062:
            return _error_result(ERR_DUPLICATE, "Duplicate equipment type")
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    except Exception as exc:
        conn.rollback()
        return _error_result(ERR_TYPE_MISMATCH, str(exc))
    finally:
        conn.close()


@app.post("/logLogin", tags=["Part3"], summary="Log Login")
def logLogin(userId: int):
    conn = get_connection()
    try:
        if not validatePermission(5, userId, {}):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")
        cur = conn.cursor()
        cur.execute("INSERT INTO Logs (UserID) VALUES (%s)", (userId,))
        conn.commit()
        return _error_result(SUCCESS_CODE, "Login logged")
    except Exception as exc:
        conn.rollback()
        return _error_result(ERR_LOGGING_FAILURE, str(exc))
    finally:
        conn.close()


@app.post("/logLogout", tags=["Part3"], summary="Log Logout")
def logLogout(userId: int):
    conn = get_connection()
    try:
        if not validatePermission(5, userId, {}):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")
        cur = conn.cursor()
        cur.execute("INSERT INTO Logs (UserID, LogOut) VALUES (%s, CURTIME())", (userId,))
        conn.commit()
        return _error_result(SUCCESS_CODE, "Logout logged")
    except Exception as exc:
        conn.rollback()
        return _error_result(ERR_LOGGING_FAILURE, str(exc))
    finally:
        conn.close()


@app.post("/logRoomAssignmentPerson", tags=["Part3"], summary="Log Room Assignment Person")
def logRoomAssignmentPerson(userId: int, buildingNumber: str, roomNumber: str, employeeEmail: str, actionType: str):
    conn = get_connection()
    try:
        affiliation = _room_affiliation(conn, buildingNumber, roomNumber)
        if not validatePermission(3, userId, affiliation):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT EmpID FROM Employees WHERE Email = %s LIMIT 1", (employeeEmail,))
        emp = cur.fetchone()
        if not emp:
            return _error_result(ERR_NOT_FOUND, "Employee not found")

        code = _log_room_assignment_person(conn, userId, buildingNumber, roomNumber, int(emp["EmpID"]), actionType)
        if code != SUCCESS_CODE:
            conn.rollback()
            return _error_result(ERR_LOGGING_FAILURE, "Log insert failed")
        conn.commit()
        return _error_result(SUCCESS_CODE, "Logged")
    finally:
        conn.close()


@app.post("/logEquipmentAssignment", tags=["Part3"], summary="Log Equipment Assignment")
def logEquipmentAssignment(userId: int, buildingNumber: str, roomNumber: str, etype: str, beforeCount: int, afterCount: int):
    conn = get_connection()
    try:
        affiliation = _room_affiliation(conn, buildingNumber, roomNumber)
        if not validatePermission(3, userId, affiliation):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT EId FROM Equipment WHERE EType = %s LIMIT 1", (etype,))
        eq = cur.fetchone()
        if not eq:
            return _error_result(ERR_NOT_FOUND, "Equipment type not found")

        code = _log_equipment_assignment(conn, userId, buildingNumber, roomNumber, int(eq["EId"]), afterCount)
        if code != SUCCESS_CODE:
            conn.rollback()
            return _error_result(ERR_LOGGING_FAILURE, "Log insert failed")
        conn.commit()
        return _error_result(SUCCESS_CODE, f"Logged before={beforeCount}, after={afterCount}")
    finally:
        conn.close()


@app.post("/logRoomDeptChange", tags=["Part3"], summary="Log Room Department Change")
def logRoomDeptChange(userId: int, buildingNumber: str, roomNumber: str, fromDept: Optional[int] = None, toDept: Optional[int] = None):
    conn = get_connection()
    try:
        affiliation = _room_affiliation(conn, buildingNumber, roomNumber)
        if toDept is not None:
            affiliation = _dept_affiliation(conn, toDept)
        if not validatePermission(3, userId, affiliation):
            return _error_result(ERR_UNAUTHORIZED, "Not allowed")

        code = _log_room_dept_change(conn, userId, buildingNumber, roomNumber, toDept)
        if code != SUCCESS_CODE:
            conn.rollback()
            return _error_result(ERR_LOGGING_FAILURE, "Log insert failed")
        conn.commit()
        return _error_result(SUCCESS_CODE, f"Logged from={fromDept} to={toDept}")
    finally:
        conn.close()

@app.get("/getLatestLog", tags=["Part3"], summary="Get Latest Log Entry")
def getLatestLog(userId: int):
    conn = get_connection()
    try:
        if not validatePermission(3, userId, {}):
            raise HTTPException(status_code=403, detail="Not allowed")
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT *
            FROM Logs
            ORDER BY ID DESC
            LIMIT 1
            """
        )
        log = cur.fetchone()
        if not log:
            raise HTTPException(status_code=404, detail="No logs found")
        return log
    finally:
        conn.close()
