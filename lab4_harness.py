from __future__ import annotations

from datetime import datetime

from api.database import get_connection_from_settings
from api.errors import SUCCESS
from api.lab4_api import (
    addEquipmentType,
    assignEquipment,
    getFloorplans,
    getRoomInfo,
    logLogin,
    logLogout,
    validatePermission,
)


def print_call(name, args):
    print("\n----------------------------------------")
    print("Function:", name)
    print("Args:", args)


def print_result(value=None, error=None):
    if error is None:
        print("Result:", value)
    else:
        print("Error:", type(error).__name__, "-", error)


def run_call(name, fn, **kwargs):
    print_call(name, kwargs)
    try:
        value = fn(**kwargs)
        print_result(value=value)
        return value
    except Exception as exc:
        print_result(error=exc)
        return None


def discover_context(conn):
    ctx = {
        "god_user": None,
        "dept_view_user": None,
        "sample_building": None,
        "sample_room": None,
    }
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT u.UserID, r.RoleName
            FROM Users u
            JOIN Roles r ON r.Role_ID = u.Role_ID
            ORDER BY u.UserID
            """
        )
        for row in cur.fetchall():
            role = row["RoleName"].lower()
            if "god" in role and ctx["god_user"] is None:
                ctx["god_user"] = row["UserID"]
            if ("department" in role or "dept" in role) and "view" in role and ctx["dept_view_user"] is None:
                ctx["dept_view_user"] = row["UserID"]

        cur.execute("SELECT BuildingNumber, RoomNumber FROM Rooms ORDER BY BuildingNumber, RoomNumber LIMIT 1")
        room = cur.fetchone()
        if room:
            ctx["sample_building"] = room["BuildingNumber"]
            ctx["sample_room"] = room["RoomNumber"]
    finally:
        cur.close()
    return ctx


def run_demo(settings_path="settings.config"):
    conn = get_connection_from_settings(settings_path)
    temp_name = "LAB4_TMP_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        ctx = discover_context(conn)
        print("CSC 366 Lab 4 demo harness")
        print("Context:", ctx)

        run_call(
            "validatePermission",
            validatePermission,
            conn=conn,
            required_permission=5,
            user_id=ctx["god_user"] or 1,
            affiliation={},
        )

        if ctx["dept_view_user"] is not None:
            run_call(
                "validatePermission",
                validatePermission,
                conn=conn,
                required_permission=2,
                user_id=ctx["dept_view_user"],
                affiliation={},
            )

        run_call(
            "getFloorplans",
            getFloorplans,
            conn=conn,
            user_id=ctx["god_user"] or ctx["dept_view_user"] or 1,
        )

        if ctx["sample_building"] and ctx["sample_room"]:
            run_call(
                "getRoomInfo",
                getRoomInfo,
                conn=conn,
                user_id=ctx["god_user"] or ctx["dept_view_user"] or 1,
                building_number=ctx["sample_building"],
                room_number=ctx["sample_room"],
            )

        if ctx["dept_view_user"] is not None:
            run_call(
                "addEquipmentType",
                addEquipmentType,
                conn=conn,
                user_id=ctx["dept_view_user"],
                equipment_type=temp_name + "_DENY",
                is_sensitive=False,
                description="Should fail permission",
            )

        add_code = run_call(
            "addEquipmentType",
            addEquipmentType,
            conn=conn,
            user_id=ctx["god_user"] or 1,
            equipment_type=temp_name,
            is_sensitive=False,
            description="Temporary test row",
        )

        if add_code == SUCCESS and ctx["sample_building"] and ctx["sample_room"]:
            run_call(
                "assignEquipment",
                assignEquipment,
                conn=conn,
                user_id=ctx["god_user"] or 1,
                building_number=ctx["sample_building"],
                room_number=ctx["sample_room"],
                equipment_identifier=temp_name,
                new_count=1,
            )
            run_call(
                "assignEquipment",
                assignEquipment,
                conn=conn,
                user_id=ctx["god_user"] or 1,
                building_number=ctx["sample_building"],
                room_number=ctx["sample_room"],
                equipment_identifier=temp_name,
                new_count=0,
            )

        run_call("logLogin", logLogin, conn=conn, user_id=ctx["god_user"] or 1)
        run_call("logLogout", logLogout, conn=conn, user_id=ctx["god_user"] or 1)
    finally:
        conn.close()


if __name__ == "__main__":
    run_demo()
