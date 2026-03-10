import configparser
import os
from datetime import datetime

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


def main():
    env = load_settings("settings.config")
    for key, val in env.items():
        os.environ[key] = str(val)

    from api import main as api_main

    client = TestClient(api_main.app)

    building, room = find_sample_room()
    temp_name = "LAB4_TMP_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    run_http(client, "GET", "/validatePermission", "validatePermission-pass", params={"required_permission": 5, "userId": 1})
    run_http(client, "GET", "/validatePermission", "validatePermission-fail", params={"required_permission": 2, "userId": 5})
    run_http(client, "GET", "/getFloorplans", "getFloorplans", params={"userId": 1})

    if building and room:
        run_http(
            client,
            "GET",
            "/getRoomInfo",
            "getRoomInfo",
            params={"userId": 1, "buildingnumber": building, "roomnumber": room},
        )

    run_http(
        client,
        "POST",
        "/addEquipmentType",
        "addEquipmentType-denied",
        params={"userId": 5},
        json_body={"EType": temp_name + "_DENY", "IsSensitive": False, "EDescription": "should fail"},
    )

    ok = run_http(
        client,
        "POST",
        "/addEquipmentType",
        "addEquipmentType-success",
        params={"userId": 1},
        json_body={"EType": temp_name, "IsSensitive": False, "EDescription": "temp row"},
    )

    if building and room and ok is not None and ok.status_code == 200:
        run_http(
            client,
            "POST",
            "/assignEquipment",
            "assignEquipment-add",
            params={"userId": 1},
            json_body={"BuildingNumber": building, "RoomNumber": room, "EType": temp_name, "NewCount": 1},
        )
        run_http(
            client,
            "POST",
            "/assignEquipment",
            "assignEquipment-remove",
            params={"userId": 1},
            json_body={"BuildingNumber": building, "RoomNumber": room, "EType": temp_name, "NewCount": 0},
        )

    run_http(client, "POST", "/logLogin", "logLogin", params={"userId": 1})
    run_http(client, "POST", "/logLogout", "logLogout", params={"userId": 1})


if __name__ == "__main__":
    main()
