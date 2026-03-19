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
    action(f"Using Administrator account {admin['Name']} to select a point on a floor with no floorplan or no room coordinates")
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

# 6. employee info

def print_employee_info(resp):
    print("\nRESPONSE:")
    print(f"  HTTP Status: {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        print(f"  Raw Response: {resp.text}")
        return

    # Handle error response
    if resp.status_code != 200:
        print(f"  Error: {data}")
        return

    print("\n  Employee Information:")
    print(f"    Name: {data.get('FullName', 'N/A')}")
    print(f"    Email: {data.get('Email', 'N/A')}")
    print(f"    Department: {data.get('DepartmentName', 'N/A')}")
    print(f"    Total Space (sq ft): {data.get('TotalSpaceSquareFeet', 0)}")

    rooms = data.get("Rooms", [])
    print(f"    Rooms Assigned: {len(rooms)}")

    if not rooms:
        print("      None")
    else:
        for i, room in enumerate(rooms, 1):
            print(f"      Room [{i}]")
            print(f"        Building: {room.get('BuildingNumber', 'N/A')}")
            print(f"        Room Number: {room.get('RoomNumber', 'N/A')}")
            print(f"        Room Type: {room.get('RoomType', 'N/A')}")
            print(f"        Room Sq Ft: {room.get('RoomSquareFeet', 0)}")
            print(f"        Employee Share: {room.get('EmployeeShareSquareFeet', 0)}")
    print()

def print_employee_info(resp):
    print("\nRESPONSE:")
    print(f"  HTTP Status: {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        print(f"  Raw Response: {resp.text}")
        return

    # Handle error response
    if resp.status_code != 200:
        print(f"  Error: {data}")
        return

    print("\n  Employee Information:")
    print(f"    Name: {data.get('FullName', 'N/A')}")
    print(f"    Email: {data.get('Email', 'N/A')}")
    print(f"    Department: {data.get('DepartmentName', 'N/A')}")
    print(f"    Total Space (sq ft): {data.get('TotalSpaceSquareFeet', 0)}")

    rooms = data.get("Rooms", [])
    print(f"    Rooms Assigned: {len(rooms)}")

    if not rooms:
        print("      None")
    else:
        for i, room in enumerate(rooms, 1):
            print(f"      Room [{i}]")
            print(f"        Building: {room.get('BuildingNumber', 'N/A')}")
            print(f"        Room Number: {room.get('RoomNumber', 'N/A')}")
            print(f"        Room Type: {room.get('RoomType', 'N/A')}")
            print(f"        Room Sq Ft: {room.get('RoomSquareFeet', 0)}")
            print(f"        Employee Share: {room.get('EmployeeShareSquareFeet', 0)}")
    print()


def get_bcsm_view_user():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT u.UserId, u.Name
            FROM Users u
            JOIN Employees e ON u.Email = e.Email
            JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
            WHERE u.Role_ID = 4 AND d.College = 'BCSM'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No BCSM view user found")
        return row
    finally:
        conn.close()


def get_other_college_view_user():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT u.UserId, u.Name
            FROM Users u
            JOIN Employees e ON u.Email = e.Email
            JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
            WHERE u.Role_ID = 4 AND d.College != 'BCSM'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No non-BCSM view user found")
        return row
    finally:
        conn.close()


def demo_employee_info():
    section("6. Employee Info")

    admin = get_admin_user()
    admin_id = admin["UserId"]

    bcsm_view_user = get_bcsm_view_user()
    bcsm_view_user_id = bcsm_view_user["UserId"]

    other_college_view_user = get_other_college_view_user()
    other_college_view_user_id = other_college_view_user["UserId"]

    employee_name = "Alan Kiste"
    employee_department = "Chemistry & Biochemistry"

    # a. Administrator access
    action(
        f"Using Administrator account {admin['Name']} to retrieve information for "
        f"{employee_name} in {employee_department}"
    )
    resp = client.get(
        "/getEmployeeInfo",
        params={
            "name": employee_name,
            "department": employee_department,
            "userId": admin_id
        }
    )
    print_employee_info(resp)

    # b. BCSM College View access
    action(
        f"Using BCSM College View account {bcsm_view_user['Name']} to retrieve information for "
        f"{employee_name} in {employee_department}"
    )
    resp = client.get(
        "/getEmployeeInfo",
        params={
            "name": employee_name,
            "department": employee_department,
            "userId": bcsm_view_user_id
        }
    )
    print_employee_info(resp)

    # c. Other college view access should fail
    action(
        f"Using non-BCSM College View account {other_college_view_user['Name']} to retrieve information for "
        f"{employee_name} in {employee_department} (should fail)"
    )
    resp = client.get(
        "/getEmployeeInfo",
        params={
            "name": employee_name,
            "department": employee_department,
            "userId": other_college_view_user_id
        }
    )
    print_employee_info(resp)

# 7. equipment locations

def print_equipment_locations(resp):
    print("\nRESPONSE:")
    print(f"  HTTP Status: {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        print(f"  Raw Response: {resp.text}")
        return

    if resp.status_code != 200:
        print(f"  Error: {data}")
        return

    print(f"\n  Equipment Type: {data.get('EType', 'N/A')}")

    locations = data.get("Locations", [])
    print(f"  Locations Found: {len(locations)}\n")

    if not locations:
        print("  No locations found.")
        return

    for i, loc in enumerate(locations, 1):
        print(f"  Location [{i}]")
        print(f"    Building: {loc.get('BuildingNumber', 'N/A')}")
        print(f"    Room: {loc.get('RoomNumber', 'N/A')}")
        print(f"    Quantity: {loc.get('Quantity', 0)}")
        print()

def demo_equipment_locations():
    section("7. Equipment Locations")

    admin = get_admin_user()
    admin_id = admin["UserId"]

    equipment_type = "ULT Freezer"

    action(
        f"Using Administrator account {admin['Name']} to retrieve locations of equipment type '{equipment_type}'"
    )

    resp = client.get(
        "/getEquipmentLocations",
        params={
            "etype": equipment_type,
            "userId": admin_id
        }
    )

    print_equipment_locations(resp)
    return resp

# 8. enhanced department list
def print_enhanced_departments(resp):
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

    print(f"  Records Returned: {len(data)}\n")

    if not data:
        print("  No departments found.")
        return

    for i, dept in enumerate(data, 1):
        print(f"  Department [{i}]")
        print(f"    DeptID: {dept.get('DeptID', 'N/A')}")
        print(f"    Department Name: {dept.get('DepartmentName', 'N/A')}")
        print(f"    Number of Assigned Rooms: {dept.get('NumAssignedRooms', 0)}")
        print(f"    Number of Rooms With Department Employees: {dept.get('NumRoomsWithDeptEmployees', 0)}")
        print(f"    Assigned Rooms Square Feet: {dept.get('AssignedRoomsSquareFeet', 0)}")
        print(f"    Employee Allocated Square Feet: {dept.get('EmployeeAllocatedSquareFeet', 0)}")
        print()

def demo_enhanced_department_list():
    section("8. Enhanced Department List")

    admin = get_admin_user()
    admin_id = admin["UserId"]

    action(f"Using Administrator account {admin['Name']} to retrieve the enhanced department list for BCSM")

    resp = client.get(
        "/getDeptListEnhanced",
        params={
            "college": "BCSM",
            "userId": admin_id
        }
    )

    print_enhanced_departments(resp)
    return resp

# 9. addition of an employee using all roles
def get_department_update_same_dept_user():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT u.UserId, u.Name
            FROM Users u
            JOIN Employees e ON u.Email = e.Email
            JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
            WHERE u.Role_ID = 3
              AND d.DepartmentName = 'Chemistry & Biochemistry'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No Chemistry Department Update user found")
        return row
    finally:
        conn.close()


def get_department_update_other_dept_user():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT u.UserId, u.Name, d.DepartmentName
            FROM Users u
            JOIN Employees e ON u.Email = e.Email
            JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
            WHERE u.Role_ID = 3
              AND d.DepartmentName <> 'Chemistry & Biochemistry'
              AND d.College = 'BCSM'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No different-department Department Update user found")
        return row
    finally:
        conn.close()


def get_bcsm_college_update_user():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT u.UserId, u.Name
            FROM Users u
            JOIN Employees e ON u.Email = e.Email
            JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
            WHERE u.Role_ID = 2
              AND d.College = 'BCSM'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No BCSM College Update user found")
        return row
    finally:
        conn.close()


def get_other_college_update_user():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT u.UserId, u.Name, d.College
            FROM Users u
            JOIN Employees e ON u.Email = e.Email
            JOIN Departments_Subdivisions d ON e.DeptID = d.DeptID
            WHERE u.Role_ID = 2
              AND d.College <> 'BCSM'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No non-BCSM College Update user found")
        return row
    finally:
        conn.close()


def get_chemistry_dept_id():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DeptID
            FROM Departments_Subdivisions
            WHERE DepartmentName = 'Chemistry & Biochemistry'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("Chemistry & Biochemistry department not found")
        return row["DeptID"]
    finally:
        conn.close()

def print_status_result(resp):
    print("\nRESPONSE:")
    print(f"  HTTP Status: {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        print(f"  Raw Response: {resp.text}")
        return

    if isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    else:
        print(f"  Data: {data}")

def demo_latest_log(admin_id, description="Retrieve latest log record"):
    action(description)
    resp = client.get(
        "/getLatestLog",
        params={"userId": admin_id}
    )
    print_result(resp)
    return resp


def demo_add_employee():
    section("9. Addition of an Employee")

    admin = get_admin_user()
    admin_id = admin["UserId"]

    bcsm_view = get_bcsm_view_user()
    same_dept_update = get_department_update_same_dept_user()
    other_dept_update = get_department_update_other_dept_user()
    bcsm_college_update = get_bcsm_college_update_user()
    other_college_update = get_other_college_update_user()

    chemistry_dept_id = get_chemistry_dept_id()

    employee_name = "Professor Demo Chemistry Employee"
    employee_email = "prof_demo_chem@calpoly.edu"

    payload = {
        "FullName": employee_name,
        "Email": employee_email,
        "DeptID": chemistry_dept_id
    }

    # a. BCSM College View - should fail
    action(
        f"Using BCSM College View account {bcsm_view['Name']} to add a Chemistry employee (should fail)"
    )
    resp = client.post(
        "/addEmployee",
        params={"userId": bcsm_view["UserId"]},
        json=payload
    )
    print_status_result(resp)

    # b. Department Update from different department - should fail
    action(
        f"Using Department Update account {other_dept_update['Name']} from a different department to add a Chemistry employee (should fail)"
    )
    resp = client.post(
        "/addEmployee",
        params={"userId": other_dept_update["UserId"]},
        json=payload
    )
    print_status_result(resp)

    # c. Department Update from same department - should succeed, then remove
    action(
        f"Using Department Update account {same_dept_update['Name']} from Chemistry & Biochemistry to add a Chemistry employee (should succeed)"
    )
    resp = client.post(
        "/addEmployee",
        params={"userId": same_dept_update["UserId"]},
        json=payload
    )
    print_status_result(resp)

    if resp.status_code == 200 and resp.json().get("ErrorCode") == "SUCCESS":
        demo_latest_log(admin_id, "Retrieve latest log record after successful same-department employee add")

        action("Removing the test Chemistry employee after successful same-department add")
        resp = client.post(
            "/removeEmployee",
            params={
                "userId": same_dept_update["UserId"],
                "email": employee_email
            }
        )
        print_status_result(resp)

        if resp.status_code == 200 and resp.json().get("ErrorCode") == "SUCCESS":
            demo_latest_log(admin_id, "Retrieve latest log record after successful same-department employee removal")

    # d. BCSM College Update - should succeed, then remove
    action(
        f"Using BCSM College Update account {bcsm_college_update['Name']} to add a Chemistry employee (should succeed)"
    )
    resp = client.post(
        "/addEmployee",
        params={"userId": bcsm_college_update["UserId"]},
        json=payload
    )
    print_status_result(resp)

    if resp.status_code == 200 and resp.json().get("ErrorCode") == "SUCCESS":
        demo_latest_log(admin_id, "Retrieve latest log record after successful BCSM College Update employee add")

        action("Removing the test Chemistry employee after successful BCSM College Update add")
        resp = client.post(
            "/removeEmployee",
            params={
                "userId": bcsm_college_update["UserId"],
                "email": employee_email
            }
        )
        print_status_result(resp)

        if resp.status_code == 200 and resp.json().get("ErrorCode") == "SUCCESS":
            demo_latest_log(admin_id, "Retrieve latest log record after successful BCSM College Update employee removal")

    # e. Other college update - should fail
    action(
        f"Using non-BCSM College Update account {other_college_update['Name']} to add a Chemistry employee (should fail)"
    )
    resp = client.post(
        "/addEmployee",
        params={"userId": other_college_update["UserId"]},
        json=payload
    )
    print_status_result(resp)

    # f. Administrator - should succeed and remain for duplicate test later
    action(
        f"Using Administrator account {admin['Name']} to add a Chemistry employee (should succeed)"
    )
    resp = client.post(
        "/addEmployee",
        params={"userId": admin_id},
        json=payload
    )
    print_status_result(resp)

    if resp.status_code == 200 and resp.json().get("ErrorCode") == "SUCCESS":
        demo_latest_log(admin_id, "Retrieve latest log record after successful administrator employee add")


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
    demo_employee_info()

    # 7. Equipment Locations
    demo_equipment_locations()
    
    # 8. Enhanced Department List
    demo_enhanced_department_list()

    # 9. Addition of an Employee using all Roles
    demo_add_employee()

    # 10. Room Assignment to a person
    

    # 11. Department Room Assignment

    # 12. Add new equipment type / assign equipment to rooms

    # 13. Duplicate entries

    return


if __name__ == "__main__":
    main()

