from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

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

app = FastAPI(title="CSC366 Lab 4 API Wrappers")


class AddEmployeeBody(BaseModel):
    full_name: str
    email: str
    dept_id: int
    position: str | None = None
    phone: str | None = None


class AssignRoomBody(BaseModel):
    employee_identifier: Any
    building_number: str
    room_number: str


class DepartmentAssignmentBody(BaseModel):
    dept_identifier: Any
    building_number: str
    room_number: str


class AssignEquipmentBody(BaseModel):
    building_number: str
    room_number: str
    equipment_identifier: Any
    new_count: int


class AddEquipmentTypeBody(BaseModel):
    equipment_type: str
    is_sensitive: bool
    description: str = ""


def _map_error_to_http(err: Exception) -> HTTPException:
    if isinstance(err, PermissionDeniedError):
        return HTTPException(status_code=403, detail="Permission denied")
    if isinstance(err, NotFoundError):
        return HTTPException(status_code=404, detail=str(err))
    return HTTPException(status_code=500, detail=str(err))


def _map_code_to_http(code: str) -> tuple[int, str]:
    if code == SUCCESS:
        return 200, code
    if code == ERR_UNAUTHORIZED:
        return 403, code
    if code == ERR_NOT_FOUND:
        return 404, code
    return 400, code


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "running"}


@app.get("/db-check")
def db_check() -> dict[str, str]:
    return {"database_connection": "successful" if test_connection() else "failed"}


@app.get("/validatePermission")
def validate_permission_route(required_permission: int, userId: int, department: list[int] | None = Query(None), college: str | None = None):
    affiliation: dict[str, Any] = {}
    if department:
        affiliation["department"] = department
    if college:
        affiliation["college"] = college
    conn = get_connection()
    try:
        return {"allowed": validatePermission(conn, required_permission, userId, affiliation)}
    finally:
        conn.close()


@app.get("/getFloorplans")
def get_floorplans_route(userId: int):
    conn = get_connection()
    try:
        return getFloorplans(conn, userId)
    except Exception as exc:
        raise _map_error_to_http(exc) from exc
    finally:
        conn.close()


@app.get("/getRooms")
def get_rooms_route(userId: int, buildingNumber: str, floorNumber: int):
    conn = get_connection()
    try:
        return getRooms(conn, userId, buildingNumber, floorNumber)
    except Exception as exc:
        raise _map_error_to_http(exc) from exc
    finally:
        conn.close()


@app.get("/findRoom")
def find_room_route(userId: int, buildingNumber: str, floorNumber: int, x: int, y: int):
    conn = get_connection()
    try:
        return findRoom(conn, userId, buildingNumber, floorNumber, x, y)
    except Exception as exc:
        raise _map_error_to_http(exc) from exc
    finally:
        conn.close()


@app.get("/getRoomInfo")
def get_room_info_route(userId: int, buildingNumber: str, roomNumber: str):
    conn = get_connection()
    try:
        return getRoomInfo(conn, userId, buildingNumber, roomNumber)
    except Exception as exc:
        raise _map_error_to_http(exc) from exc
    finally:
        conn.close()


@app.get("/getDeptList")
def get_dept_list_route(userId: int, collegeName: str):
    conn = get_connection()
    try:
        return getDeptList(conn, userId, collegeName)
    except Exception as exc:
        raise _map_error_to_http(exc) from exc
    finally:
        conn.close()


@app.get("/getEmployees")
def get_employees_route(userId: int, collegeName: str, departmentName: str):
    conn = get_connection()
    try:
        return getEmployees(conn, userId, collegeName, departmentName)
    except Exception as exc:
        raise _map_error_to_http(exc) from exc
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
    identifier: Any
    if email:
        identifier = {"email": email}
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
        raise _map_error_to_http(exc) from exc
    finally:
        conn.close()


@app.get("/getEquipmentLocations")
def get_equipment_locations_route(userId: int, equipmentIdentifier: str):
    conn = get_connection()
    try:
        return getEquipmentLocations(conn, userId, equipmentIdentifier)
    except Exception as exc:
        raise _map_error_to_http(exc) from exc
    finally:
        conn.close()


@app.get("/getSensitiveEquipmentLocations")
def get_sensitive_equipment_locations_route(userId: int, collegeName: str):
    conn = get_connection()
    try:
        return getSensitiveEquipmentLocations(conn, userId, collegeName)
    except Exception as exc:
        raise _map_error_to_http(exc) from exc
    finally:
        conn.close()


@app.post("/addEmployee")
def add_employee_route(userId: int, body: AddEmployeeBody):
    conn = get_connection()
    try:
        code = addEmployee(conn, userId, body.full_name, body.email, body.dept_id, body.position, body.phone)
    finally:
        conn.close()
    status, detail = _map_code_to_http(code)
    if status != 200:
        raise HTTPException(status_code=status, detail=detail)
    return {"code": code}


@app.post("/assignRoom")
def assign_room_route(userId: int, body: AssignRoomBody):
    conn = get_connection()
    try:
        code = assignRoom(conn, userId, body.employee_identifier, body.building_number, body.room_number)
    finally:
        conn.close()
    status, detail = _map_code_to_http(code)
    if status != 200:
        raise HTTPException(status_code=status, detail=detail)
    return {"code": code}


@app.post("/removeRoomAssignment")
def remove_room_assignment_route(userId: int, body: AssignRoomBody):
    conn = get_connection()
    try:
        code = removeRoomAssignment(conn, userId, body.employee_identifier, body.building_number, body.room_number)
    finally:
        conn.close()
    status, detail = _map_code_to_http(code)
    if status != 200:
        raise HTTPException(status_code=status, detail=detail)
    return {"code": code}


@app.post("/departmentAssignment")
def department_assignment_route(userId: int, body: DepartmentAssignmentBody):
    conn = get_connection()
    try:
        code = departmentAssignment(conn, userId, body.dept_identifier, body.building_number, body.room_number)
    finally:
        conn.close()
    status, detail = _map_code_to_http(code)
    if status != 200:
        raise HTTPException(status_code=status, detail=detail)
    return {"code": code}


@app.post("/assignEquipment")
def assign_equipment_route(userId: int, body: AssignEquipmentBody):
    conn = get_connection()
    try:
        code = assignEquipment(conn, userId, body.building_number, body.room_number, body.equipment_identifier, body.new_count)
    finally:
        conn.close()
    status, detail = _map_code_to_http(code)
    if status != 200:
        raise HTTPException(status_code=status, detail=detail)
    return {"code": code}


@app.post("/addEquipmentType")
def add_equipment_type_route(userId: int, body: AddEquipmentTypeBody):
    conn = get_connection()
    try:
        code = addEquipmentType(conn, userId, body.equipment_type, body.is_sensitive, body.description)
    finally:
        conn.close()
    status, detail = _map_code_to_http(code)
    if status != 200:
        raise HTTPException(status_code=status, detail=detail)
    return {"code": code}


@app.post("/logLogin")
def log_login_route(userId: int):
    conn = get_connection()
    try:
        code = logLogin(conn, userId)
    finally:
        conn.close()
    status, detail = _map_code_to_http(code)
    if status != 200:
        raise HTTPException(status_code=status, detail=detail)
    return {"code": code}


@app.post("/logLogout")
def log_logout_route(userId: int):
    conn = get_connection()
    try:
        code = logLogout(conn, userId)
    finally:
        conn.close()
    status, detail = _map_code_to_http(code)
    if status != 200:
        raise HTTPException(status_code=status, detail=detail)
    return {"code": code}
