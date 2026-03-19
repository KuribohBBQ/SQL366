from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.database import get_connection

load_dotenv()

from api import main as api_main

client = TestClient(api_main.app)


def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_result(resp):
    print("\nRESPONSE:")
    print(f"  HTTP Status: {resp.status_code}")
    try:
        data = resp.json()
    except Exception:
        print(f"  Raw Response: {resp.text}")
        return

    if isinstance(data, list):
        print(f"  Records Returned: {len(data)}")
        for i, item in enumerate(data, 1):
            print(f"    [{i}] {item}")
    elif isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    else:
        print(f"  Data: {data}")


def get_admin_user():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT UserId, Name
            FROM Users
            WHERE Name = 'Michael Black'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No admin user found")
        return row
    finally:
        conn.close()


def get_latest_log(admin_id):
    print("\nLATEST LOG RECORD:")
    resp = client.get("/getLatestLog", params={"userId": admin_id})
    print_result(resp)


def main():
    # 1. establish DB connection / access database instance
    section("Instructor Demo Test Harness")

    conn = get_connection()
    try:
        print("Connected to database successfully.")
    finally:
        conn.close()

    # 2. set the database user / user role
    admin = get_admin_user()
    admin_id = admin["UserId"]

    print(f"Using user: {admin['Name']}")
    print(f"UserId: {admin_id}")
    print("Role: Administrator")

    # 3. print some text describing the test
    print("\nTEST DESCRIPTION:")
    print("Run one isolated API call and inspect the result.")

    # 4. call an API function

    resp = client.get(
        "/getDeptList",
        params={
            "college": "BCSM",
            "userId": admin_id
        }
    )

    print_result(resp)

    get_latest_log(admin_id)


if __name__ == "__main__":
    main()