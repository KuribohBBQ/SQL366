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



def main():
    # 1. List of Departments
    demo_list_departments()

    # 2. List of Floorplans
    demo_list_floorplans()

    # 3. List of Rooms
    demo_list_rooms()

    # 4. Room Selection API

    # 5. List of Employees

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

