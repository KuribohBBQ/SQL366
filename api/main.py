from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query

from api.database import get_connection, test_connection
from api.errors import ERR_NOT_FOUND, ERR_UNAUTHORIZED, SUCCESS
from api.lab4_api import (
    NotFoundError,
    PermissionDeniedError,
    addEmployee,
    addEquipmentType,
    assignEquipment,
    assignRoom,
    departmentAssignment,
    findRoom,
    getDeptList,
    getEmployeeInfo,
    getEmployees,
    getEquipmentLocations,
    getFloorplans,
    getRoomInfo,
    getRooms,
    getSensitiveEquipmentLocations,
    logLogin,
    logLogout,
    removeRoomAssignment,
    validatePermission,
)

app = FastAPI()


def _raise_from_error(exc: Exception):
    if isinstance(exc, PermissionDeniedError):
        raise HTTPException(status_code=403, detail="Permission denied") from exc
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    raise HTTPException(status_code=500, detail=str(exc)) from exc


def _return_code_or_error(code: str):
    if code == SUCCESS:
        return {"code": SUCCESS}
    if code == ERR_UNAUTHORIZED:
        raise HTTPException(status_code=403, detail=code)
    if code == ERR_NOT_FOUND:
        raise HTTPException(status_code=404, detail=code)
    raise HTTPException(status_code=400, detail=code)


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/db-check")
def db_check():
    return {"database_connection": "successful" if test_connection() else "failed"}


@app.get("/validatePermission")
def validate_permission_route(
    required_permission: int,
    userId: int,
    department: list[int] | None = Query(None),
    college: str | None = None,
):
    affiliation: dict[str, Any] = {}
    if department:
        affiliation["department"] = department
    if college:
        affiliation["college"] = college

    conn = get_connection()
    try:
        allowed = validatePermission(conn, required_permission, userId, affiliation)
        return {"allowed": allowed}
    finally:
        conn.close()


@app.get("/getFloorplans")
def get_floorplans_route(userId: int):
    conn = get_connection()
    try:
        return getFloorplans(conn, userId)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.get("/getRooms")
def get_rooms_route(userId: int, buildingNumber: str, floorNumber: int):
    conn = get_connection()
    try:
        return getRooms(conn, userId, buildingNumber, floorNumber)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.get("/findRoom")
def find_room_route(userId: int, buildingNumber: str, floorNumber: int, x: int, y: int):
    conn = get_connection()
    try:
        return findRoom(conn, userId, buildingNumber, floorNumber, x, y)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.get("/getRoomInfo")
def get_room_info_route(userId: int, buildingNumber: str, roomNumber: str):
    conn = get_connection()
    try:
        return getRoomInfo(conn, userId, buildingNumber, roomNumber)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.get("/getDeptList")
def get_dept_list_route(userId: int, collegeName: str):
    conn = get_connection()
    try:
        return getDeptList(conn, userId, collegeName)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.get("/getEmployees")
def get_employees_route(userId: int, collegeName: str, departmentName: str):
    conn = get_connection()
    try:
        return getEmployees(conn, userId, collegeName, departmentName)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.get("/getEmployeeInfo")
def get_employee_info_route(
    userId: int,
    email: str | None = None,
    name: str | None = None,
    department: str | None = None,
    college: str | None = None,
):
    if email:
        identifier: Any = {"email": email}
    elif name and department:
        identifier = {"name": name, "department": department, "college": college}
    elif name:
        identifier = {"name": name}
    else:
        raise HTTPException(status_code=400, detail="Provide email or name")

    conn = get_connection()
    try:
        return getEmployeeInfo(conn, userId, identifier)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.get("/getEquipmentLocations")
def get_equipment_locations_route(userId: int, equipmentIdentifier: str):
    conn = get_connection()
    try:
        return getEquipmentLocations(conn, userId, equipmentIdentifier)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.get("/getSensitiveEquipmentLocations")
def get_sensitive_equipment_locations_route(userId: int, collegeName: str):
    conn = get_connection()
    try:
        return getSensitiveEquipmentLocations(conn, userId, collegeName)
    except Exception as exc:
        _raise_from_error(exc)
    finally:
        conn.close()


@app.post("/addEmployee")
def add_employee_route(userId: int, body: dict[str, Any]):
    conn = get_connection()
    try:
        code = addEmployee(
            conn,
            userId,
            body.get("full_name"),
            body.get("email"),
            body.get("dept_id"),
            body.get("position"),
            body.get("phone"),
        )
    finally:
        conn.close()
    return _return_code_or_error(code)


@app.post("/assignRoom")
def assign_room_route(userId: int, body: dict[str, Any]):
    conn = get_connection()
    try:
        code = assignRoom(
            conn,
            userId,
            body.get("employee_identifier"),
            body.get("building_number"),
            body.get("room_number"),
        )
    finally:
        conn.close()
    return _return_code_or_error(code)


@app.post("/removeRoomAssignment")
def remove_room_assignment_route(userId: int, body: dict[str, Any]):
    conn = get_connection()
    try:
        code = removeRoomAssignment(
            conn,
            userId,
            body.get("employee_identifier"),
            body.get("building_number"),
            body.get("room_number"),
        )
    finally:
        conn.close()
    return _return_code_or_error(code)


@app.post("/departmentAssignment")
def department_assignment_route(userId: int, body: dict[str, Any]):
    conn = get_connection()
    try:
        code = departmentAssignment(
            conn,
            userId,
            body.get("dept_identifier"),
            body.get("building_number"),
            body.get("room_number"),
        )
    finally:
        conn.close()
    return _return_code_or_error(code)


@app.post("/assignEquipment")
def assign_equipment_route(userId: int, body: dict[str, Any]):
    conn = get_connection()
    try:
        code = assignEquipment(
            conn,
            userId,
            body.get("building_number"),
            body.get("room_number"),
            body.get("equipment_identifier"),
            body.get("new_count"),
        )
    finally:
        conn.close()
    return _return_code_or_error(code)


@app.post("/addEquipmentType")
def add_equipment_type_route(userId: int, body: dict[str, Any]):
    conn = get_connection()
    try:
        code = addEquipmentType(
            conn,
            userId,
            body.get("equipment_type"),
            body.get("is_sensitive"),
            body.get("description", ""),
        )
    finally:
        conn.close()
    return _return_code_or_error(code)


@app.post("/logLogin")
def log_login_route(userId: int):
    conn = get_connection()
    try:
        code = logLogin(conn, userId)
    finally:
        conn.close()
    return _return_code_or_error(code)


@app.post("/logLogout")
def log_logout_route(userId: int):
    conn = get_connection()
    try:
        code = logLogout(conn, userId)
    finally:
        conn.close()
    return _return_code_or_error(code)
