import configparser
import os
from datetime import datetime
from typing import Dict, Any

from fastapi.testclient import TestClient


def load_settings(path="settings.config"):
    if not os.path.exists(path):
        raise FileNotFoundError("missing settings.config")
    parser = configparser.ConfigParser()
    parser.read(path)
    if parser.has_section("mysql"):
        section = parser["mysql"]
        return {
            "DB_HOST": section.get("host", ""),
            "DB_PORT": section.get("port", "3306"),
            "DB_USER": section.get("user", ""),
            "DB_PASSWORD": section.get("password", ""),
            "DB_NAME": section.get("database", ""),
        }
    values = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            values[k.strip().lower()] = v.strip()
    return {
        "DB_HOST": values.get("host", ""),
        "DB_PORT": values.get("port", "3306"),
        "DB_USER": values.get("user", ""),
        "DB_PASSWORD": values.get("password", ""),
        "DB_NAME": values.get("database", ""),
    }


def print_call(name, args):
    print("\n------------------------")
    print("Function:", name)
    print("Args:", args)


def print_result(status, body):
    print("HTTP:", status)
    print("Result:", body)


def run_http(client, method, path, name, params=None, json_body=None):
    args = {"params": params, "json": json_body}
    print_call(name, args)
    try:
        if method == "GET":
            resp = client.get(path, params=params)
        else:
            resp = client.post(path, params=params, json=json_body)
        print_result(resp.status_code, resp.json())
        return resp
    except Exception as exc:
        print("Error:", str(exc))
        return None


def find_sample_room():
    from api.database import get_connection

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT BuildingNumber, RoomNumber FROM Rooms ORDER BY BuildingNumber, RoomNumber LIMIT 1")
        row = cur.fetchone()
        if not row:
            return None, None
        return row["BuildingNumber"], row["RoomNumber"]
    finally:
        conn.close()

def get_admin_user() -> Dict[str, Any]:
    from api.database import get_connection

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT UserId FROM Users WHERE Name = 'Michael Black' LIMIT 1")
        row = cur.fetchone()
        if not row:
            raise ValueError("No admin user found in database")
        print(row)
        return row
    finally:
        conn.close()

def get_bcsm_view_user() -> Dict[str, Any]:
    from api.database import get_connection

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
                    SELECT u.UserId
                    FROM Users u
                    JOIN Employees e ON u.Email = e.Email
                    JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
                    WHERE u.Role_ID = 4 and d.College = 'BCSM'
                        LIMIT 1
                    """
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("No BCSM college view user found in database")
        print(row)
        return row
    finally:
        conn.close()

def get_ceng_view_user() -> Dict[str, Any]:
    from api.database import get_connection

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
                    SELECT u.UserId
                    FROM Users u
                    JOIN Employees e ON u.Email = e.Email
                    JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
                    WHERE u.Role_ID = 4 and d.College = 'CENG'
                        LIMIT 1
                    """
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("No CENG college view user found in database")
        print(row)
        return row
    finally:
        conn.close()

def get_bio_sci_update_user() -> Dict[str, Any]:
    from api.database import get_connection

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
                    SELECT u.UserId
                    FROM Users u
                    JOIN Employees e ON u.Email = e.Email
                    WHERE u.Role_ID = 3 and e.DeptID = 115100
                        LIMIT 1
                    """
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("No BCSM college update user found in database")
        print(row)
        return row
    finally:
        conn.close()

def get_csc_update_user() -> Dict[str, Any]:
    from api.database import get_connection

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
                    SELECT u.UserId
                    FROM Users u
                    JOIN Employees e ON u.Email = e.Email
                    WHERE u.Role_ID = 3 and e.DeptID = 111500
                        LIMIT 1
                    """
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("No CENG college update user found in database")
        print(row)
        return row
    finally:
        conn.close()

def get_bcsm_update_user() -> Dict[str, Any]:
    from api.database import get_connection

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
                    SELECT u.UserId
                    FROM Users u
                    JOIN Employees e ON u.Email = e.Email
                    JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
                    WHERE u.Role_ID = 2 and d.College = 'BCSM'
                        LIMIT 1
                    """
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("No BCSM college update user found in database")
        print(row)
        return row
    finally:
        conn.close()

def print_employees(employee_list):
    if not employee_list:
        print("No employees found.")
        return

    for emp in employee_list:
        print(f"\nName: {emp['FullName']}")
        print(f"Email: {emp['Email']}")
        print(f"Total Space: {emp['TotalSpaceSquareFeet']}")
        print("Rooms:")
        if not emp["Rooms"]:
            print("  None")
        else:
            for room in emp["Rooms"]:
                print(
                    f"  {room['BuildingNumber']} {room['RoomNumber']} "
                    f"(Share: {room['EmployeeShareSquareFeet']})"
                )

def main():
    env = load_settings("settings.config")
    for key, val in env.items():
        os.environ[key] = str(val)

    from api import main as api_main

    client = TestClient(api_main.app)

    building, room = find_sample_room()
    temp_name = "LAB4_TMP_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    # EX: Get list of Departments
    admin = get_admin_user()
    admin_id = admin["UserId"]
    run_http(client, "GET", "/getDeptList", "Get Department List", params={"college": "BCSM", "userId": admin_id})

    # EX: Get list of Floorplans
    run_http(client, "GET", "/getFloorplans", "Get Floorplan List", params={"userId": admin_id})

    # EX: Get list of Rooms
    run_http(client, "GET", "/getRooms", "Get Room List", params={"buildingnumber": building, "floornumber": 3, "userId": admin_id})

    #EX: Room Selection
    run_http(client, "GET", "/findRoom", "Find Room", params={"buildingnumber": building, "floornumber": 3, "x": 220, "y": 80, "userId": admin_id})

    #EX: Room Selection Overlapping
    run_http(client, "GET", "/findRoom", "Find Room Overlapping", params={"buildingnumber": building, "floornumber": 3, "x": 220, "y": 91, "userId": admin_id})

    #EX: Room Selection Out of Bounds
    run_http(client, "GET", "/findRoom", "Find Room Out of Bounds", params={"buildingnumber": building, "floornumber": 3, "x": 500, "y": 500, "userId": admin_id})

    #EX: Room Selection No Floorplan
    run_http(client, "GET", "/findRoom", "Find Room No Floorplan", params={"buildingnumber": building, "floornumber": 1, "x": 220, "y": 80, "userId": admin_id})

    #EX: Get List of Employees in a Department
    resp = run_http(
    client,
    "GET",
    "/getEmployees",
    "Get Employees in Department",
    params={
        "college": "BCSM",
        "department": "Biological Sciences",
        "userId": admin_id
    }
    )
    if resp and resp.status_code == 200:
        print_employees(resp.json())

    
    #EX: Employee Search Admin View
    run_http(client, "GET", "/getEmployeeInfo", "Get Employee Info Admin", params={"name": "Mallary Greenlee-Wacker", "department": "Biological Sciences", "userId": admin_id})

    #EX: Employee Search BCSM View
    bcsm_view_user = get_bcsm_view_user()
    bcsm_user_id = bcsm_view_user["UserId"]

    run_http(client, "GET", "/getEmployeeInfo", "Get Employee Info BCSM View", params={"name": "Mallary Greenlee-Wacker", "department": "Biological Sciences", "userId": bcsm_user_id})

    #EX: Employee Search CENG View - Should not return results for BCSM employee
    ceng_view_user = get_ceng_view_user()
    ceng_user_id = ceng_view_user["UserId"]
    run_http(client, "GET", "/getEmployeeInfo", "Get Employee Info CENG View", params={"name": "Mallary Greenlee-Wacker", "department": "Biological Sciences", "userId": ceng_user_id})

    #EX: Equipment Search Admin View
    run_http(client, "GET", "/getEquipmentLocations", "Get Equipment Locations Admin", params={"etype": "ULT Freezer", "userId": admin_id})
    
    #EX: Get Enhanced Departments List
    run_http(client, "GET", "/getDeptListEnhanced", "Get Enhanced Department List", params={"college": "BCSM", "userId": admin_id})

    #EX: Add Biological Sciences Employee, College View
    employee_name = "John Doe"
    employee_email = "jdoe@example.com"
    run_http(client, "POST", "/addEmployee", "Add Employee BCSM View", params={"userId": bcsm_user_id}, json_body={"FullName": employee_name, "Email": employee_email, "DeptID": 115100})

    #EX: Add Biological Sciences Employee, Wrong Department Update View
    csc_update_user = get_csc_update_user()
    csc_update_user_id = csc_update_user["UserId"]
    run_http(client, "POST", "/addEmployee", "Add Employee CENG Update View (Wrong Dept)", params={"userId": csc_update_user_id}, json_body={"FullName": employee_name, "Email": employee_email, "DeptID": 115100})

    #EX: Add Biological Sciences Employee, Correct Department Update View
    bio_sci_update_user = get_bio_sci_update_user()
    bio_sci_update_user_id = bio_sci_update_user["UserId"]
    run_http(client, "POST", "/addEmployee", "Add Employee BCSM Update View (Correct Dept)", params={"userId": bio_sci_update_user_id}, json_body={"FullName": employee_name, "Email": employee_email, "DeptID": 115100})
    #Remove the test employee after demo
    run_http(client, "POST", "/removeEmployee", "Remove Test Employee BCSM Update View", params={"userId": bio_sci_update_user_id, "email": employee_email})

    #EX: Add Biological Sciences Employee, BCSM College Update View
    bcsm_update_user = get_bcsm_update_user()
    bcsm_update_user_id = bcsm_update_user["UserId"]
    run_http(client, "POST", "/addEmployee", "Add Employee BCSM College Update View", params={"userId": bcsm_update_user_id}, json_body={"FullName": employee_name, "Email": employee_email, "DeptID": 115100})
    #Remove the test employee after demo
    run_http(client, "POST", "/removeEmployee", "Remove Test Employee BCSM College Update View", params={"userId": bcsm_update_user_id, "email": employee_email})

    #EX: Add Biological Sciences Employee, Admin Update View
    # run_http(client, "POST", "/addEmployee", "Add Employee Admin Update View", params={"userId": admin_id}, json_body={"FullName": employee_name, "Email": employee_email, "DeptID": 115100})



if __name__ == "__main__":
    main()