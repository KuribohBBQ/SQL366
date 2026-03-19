from dotenv import load_dotenv
import os
from fastapi.testclient import TestClient

load_dotenv()

from api import main as api_main
from api.database import get_connection

client = TestClient(api_main.app)

# printing system
def section(title):
    print("\n" + "=" * 140)
    print(f"SECTION: {title}")
    print("=" * 140)

def action(description):
    print("\n" + "-" * 140)
    print(f"ACTION: {description}")
    print("-" * 140)

def params_block(params):
    print("PARAMETERS: ")
    if not params:
        print("  None")
        return
    for k, v, in params.items():
        print(f"  {k}: {v}")

def print_result(resp, limit=None):
    print("\nRESPONSE:")
    print(f"  HTTP Status: {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        print(f"  Raw Response: {resp.text}")
        return

    # Handle list responses
    if isinstance(data, list):
        print(f"  Records Returned: {len(data)}\n")

        items = data if limit is None else data[:limit]

        for i, item in enumerate(items, 1):
            print(f"    [{i}] {item}")

        if limit is not None and len(data) > limit:
            print(f"\n  ... showing {limit} of {len(data)} records ...")

    # Handle dictionary responses
    elif isinstance(data, dict):
        print()
        for k, v in data.items():
            print(f"  {k}: {v}")

    # Fallback
    else:
        print(f"  Data: {data}")

def run_get(path, description, params=None):
    action(description)
    params_block(params)

    resp = client.get(path, params=params)

    print_result(resp)
    return resp

def get_admin_user():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT UserId, Name, Email
            FROM Users
            WHERE Name = 'Michael Black'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No admin user found in database")
        return row
    finally:
        conn.close()

# 1. list of departments

def demo_list_departments():
    section("1. List of Departments")

    admin = get_admin_user()
    admin_id = admin["UserId"]

    action(f"Using Administrator account {admin['Name']} to retrieve departments in BCSM")
    resp = client.get(
        "/getDeptList",
        params={
            "college": "BCSM",
            "userId": admin_id
        }
    )

    print_result(resp)

    return resp

# 2. list of floorplans

def demo_list_floorplans():
    section("2. List of Floorplans")

    admin = get_admin_user()
    admin_id = admin["UserId"]
    
    action(f"Using Administrator account {admin['Name']} to retrieve all floorplans")
    resp = client.get(
        "/getFloorplans",
        params={
            "userId": admin_id
        }
    )

    print_result(resp)
    return resp

# 3. list of rooms

def demo_list_rooms():
    section("3. List of Rooms")

    admin = get_admin_user()
    admin_id = admin["UserId"]

    action(f"Using Administrator account {admin['Name']} to retrieve all rooms on floor 3 of Fisher and Science")
    resp = client.get(
        "/getRooms",
        params={
            "buildingnumber" : "033-0",
            "floornumber" : 3,
            "userId" : admin_id
        }
    )

    print_result(resp)
    return resp

# 4. room selection api

def demo_room_selection():
    section("4. Room Selection API")

    admin = get_admin_user()
    admin_id = admin["UserId"]

    # a. Point inside a single room
    action(f"Using Administrator account {admin['Name']} to select a point inside a single room")
    resp = client.get(
        "/findRoom",
        params={
            "buildingnumber": "033-0",
            "floornumber": 3,
            "x": 220,
            "y": 80,
            "userId": admin_id
        }
    )
    print_result(resp)

    # b. Point inside overlapping rooms
    action(f"Using Administrator account {admin['Name']} to select a point inside overlapping rooms")
    resp = client.get(
        "/findRoom",
        params={
            "buildingnumber": "033-0",
            "floornumber": 3,
            "x": 220,
            "y": 91,
            "userId": admin_id
        }
    )
    print_result(resp)

    # c. Point outside all rooms
    action(f"Using Administrator account {admin['Name']} to select a point outside all rooms")
    resp = client.get(
        "/findRoom",
        params={
            "buildingnumber": "033-0",
            "floornumber": 3,
            "x": 500,
            "y": 500,
            "userId": admin_id
        }
    )
    print_result(resp)

    # d. Floor with no floorplan / no bounding boxes
    action(f"Using Administrator account {admin['Name']}t to select a point on a floor with no floorplan or no room coordinates")
    resp = client.get(
        "/findRoom",
        params={
            "buildingnumber": "033-0",
            "floornumber": 1,
            "x": 220,
            "y": 80,
            "userId": admin_id
        }
    )
    print_result(resp)
    

# 5. print employees

def print_employees_result(resp):
    print("\nRESPONSE:")
    print(f"  HTTP Status: {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        print(f"  Raw Response: {resp.text}")
        return

    if not isinstance(data, list):
        print(f"  Data: {data}")
        return

    print(f"  Employees Returned: {len(data)}\n")

    if not data:
        print("  No employees found.")
        return

    for i, emp in enumerate(data, 1):
        print(f"  Employee [{i}]")
        print(f"    Name: {emp.get('FullName', 'N/A')}")
        print(f"    Email: {emp.get('Email', 'N/A')}")
        print(f"    Total Space (sq ft): {emp.get('TotalSpaceSquareFeet', 0)}")

        rooms = emp.get("Rooms", [])
        print(f"    Rooms Assigned: {len(rooms)}")

        if not rooms:
            print("      None")
        else:
            for j, room in enumerate(rooms, 1):
                print(f"      Room [{j}]")
                print(f"        Building: {room.get('BuildingNumber', 'N/A')}")
                print(f"        Room Number: {room.get('RoomNumber', 'N/A')}")
                print(f"        Employee Share (sq ft): {room.get('EmployeeShareSquareFeet', 0)}")
        print()

def demo_list_employees():
    section("5. List of Employees")

    admin = get_admin_user()
    admin_id = admin["UserId"]

    action(f"Using Administrator account {admin['Name']} to retrieve employees in Chemistry Department of BCSM")

    resp = client.get(
        "/getEmployees",
        params={
            "college": "BCSM",
            "department": "Chemistry & Biochemistry",
            "userId": admin_id
        }
    )

    print_employees_result(resp)
    return resp
    


def main():
    # 1. List of Departments
    demo_list_departments()

    # 2. List of Floorplans
    demo_list_floorplans()

    # 3. List of Rooms
    demo_list_rooms()

    # 4. Room Selection API
    demo_room_selection()

    # 5. List of Employees
    demo_list_employees()

    # 6. Employee Info
    

    # 7. Equipment Locations

    # 8. Enhanced Department List

    # 9. Addition of an Employee using all Roles

    # 10. Room Assignment to a person

    # 11. Department Room Assignment

    # 12. Add new equipment type / assign equipment to rooms

    # 13. Duplicate entries

    return


if __name__ == "__main__":
    main()

