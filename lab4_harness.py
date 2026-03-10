from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pprint import pformat
from typing import Any, Callable

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


@dataclass
class DemoContext:
    god_user: int | None = None
    college_update_user: int | None = None
    dept_update_user: int | None = None
    dept_view_user: int | None = None
    sample_building: str | None = None
    sample_room: str | None = None


def _print_call(function_name: str, kwargs: dict[str, Any]) -> None:
    print(f"\n=== CALL {function_name} ===")
    print(f"args={pformat(kwargs)}")


def _print_result(result: Any = None, error: Exception | None = None) -> None:
    if error is None:
        print(f"result={pformat(result)}")
    else:
        print(f"exception={type(error).__name__}: {error}")


def run_call(function_name: str, fn: Callable[..., Any], **kwargs: Any) -> Any:
    _print_call(function_name, kwargs)
    try:
        result = fn(**kwargs)
        _print_result(result=result)
        return result
    except Exception as exc:
        _print_result(error=exc)
        return None


def discover_context(conn) -> DemoContext:
    ctx = DemoContext()
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
        users = cur.fetchall()
        for row in users:
            role = row["RoleName"].lower()
            if "god" in role and ctx.god_user is None:
                ctx.god_user = row["UserID"]
            if "college" in role and "update" in role and ctx.college_update_user is None:
                ctx.college_update_user = row["UserID"]
            if ("department" in role or "dept" in role) and "update" in role and ctx.dept_update_user is None:
                ctx.dept_update_user = row["UserID"]
            if ("department" in role or "dept" in role) and "view" in role and ctx.dept_view_user is None:
                ctx.dept_view_user = row["UserID"]

        cur.execute("SELECT BuildingNumber, RoomNumber FROM Rooms ORDER BY BuildingNumber, RoomNumber LIMIT 1")
        room = cur.fetchone()
        if room:
            ctx.sample_building = room["BuildingNumber"]
            ctx.sample_room = room["RoomNumber"]
    finally:
        cur.close()
    return ctx


def run_demo(settings_path: str = "settings.config") -> None:
    conn = get_connection_from_settings(settings_path)
    temp_equipment_name = f"LAB4_TMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        ctx = discover_context(conn)
        print("=== CSC 366 Lab 4 Harness ===")
        print(pformat(ctx))

        if ctx.god_user is None:
            print("No God-level user found. Harness will still run what it can.")
        if ctx.dept_view_user is None:
            print("No Department View user found. Permission-failure demo may be limited.")

        run_call(
            "validatePermission",
            validatePermission,
            conn=conn,
            required_permission=5,
            user_id=ctx.god_user or 1,
            affiliation={},
        )

        if ctx.dept_view_user is not None:
            run_call(
                "validatePermission",
                validatePermission,
                conn=conn,
                required_permission=2,
                user_id=ctx.dept_view_user,
                affiliation={},
            )

        run_call(
            "getFloorplans",
            getFloorplans,
            conn=conn,
            user_id=ctx.god_user or ctx.dept_view_user or 1,
        )

        if ctx.sample_building and ctx.sample_room:
            run_call(
                "getRoomInfo",
                getRoomInfo,
                conn=conn,
                user_id=ctx.god_user or ctx.dept_view_user or 1,
                building_number=ctx.sample_building,
                room_number=ctx.sample_room,
            )

        if ctx.dept_view_user is not None:
            run_call(
                "addEquipmentType",
                addEquipmentType,
                conn=conn,
                user_id=ctx.dept_view_user,
                equipment_type=f"{temp_equipment_name}_DENY",
                is_sensitive=False,
                description="Expected unauthorized test",
            )

        add_code = run_call(
            "addEquipmentType",
            addEquipmentType,
            conn=conn,
            user_id=ctx.god_user or 1,
            equipment_type=temp_equipment_name,
            is_sensitive=False,
            description="Temporary harness equipment",
        )

        if add_code == SUCCESS and ctx.sample_building and ctx.sample_room:
            run_call(
                "assignEquipment",
                assignEquipment,
                conn=conn,
                user_id=ctx.god_user or 1,
                building_number=ctx.sample_building,
                room_number=ctx.sample_room,
                equipment_identifier=temp_equipment_name,
                new_count=1,
            )
            run_call(
                "assignEquipment",
                assignEquipment,
                conn=conn,
                user_id=ctx.god_user or 1,
                building_number=ctx.sample_building,
                room_number=ctx.sample_room,
                equipment_identifier=temp_equipment_name,
                new_count=0,
            )

        run_call("logLogin", logLogin, conn=conn, user_id=ctx.god_user or 1)
        run_call("logLogout", logLogout, conn=conn, user_id=ctx.god_user or 1)
    finally:
        conn.close()


if __name__ == "__main__":
    run_demo()
