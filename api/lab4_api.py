from __future__ import annotations

from decimal import Decimal
from typing import Any

try:
    from mysql.connector import Error, IntegrityError
except ModuleNotFoundError:
    class Error(Exception):
        pass

    class IntegrityError(Error):
        pass

from api.errors import (
    ERR_DUPLICATE,
    ERR_FK_VIOLATION,
    ERR_LOGGING_FAILURE,
    ERR_NOT_FOUND,
    ERR_TYPE_MISMATCH,
    ERR_UNAUTHORIZED,
    SUCCESS,
)


class PermissionDeniedError(Exception):
    pass


class NotFoundError(Exception):
    pass


PERM_GOD = 1
PERM_COLLEGE_UPDATE = 2
PERM_DEPT_UPDATE = 3
PERM_COLLEGE_VIEW = 4
PERM_DEPT_VIEW = 5


def _normalize_text(value: Any) -> str:
    return "".join(ch for ch in str(value).lower() if ch.isalnum() or ch.isspace()).strip()


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _map_mysql_error(exc: Error) -> str:
    if getattr(exc, "errno", None) in {1062}:
        return ERR_DUPLICATE
    if getattr(exc, "errno", None) in {1451, 1452}:
        return ERR_FK_VIOLATION
    if getattr(exc, "errno", None) in {1292, 1366}:
        return ERR_TYPE_MISMATCH
    return ERR_TYPE_MISMATCH


def _role_name_to_rank(role_name: str | None) -> int | None:
    if not role_name:
        return None
    normalized = _normalize_text(role_name)
    if "god" in normalized:
        return PERM_GOD
    if "college" in normalized and "update" in normalized:
        return PERM_COLLEGE_UPDATE
    if ("department" in normalized or "dept" in normalized) and "update" in normalized:
        return PERM_DEPT_UPDATE
    if "college" in normalized and "view" in normalized:
        return PERM_COLLEGE_VIEW
    if ("department" in normalized or "dept" in normalized) and "view" in normalized:
        return PERM_DEPT_VIEW
    return None


def _resolve_required_rank(required_permission: int | str) -> int | None:
    if isinstance(required_permission, int):
        if PERM_GOD <= required_permission <= PERM_DEPT_VIEW:
            return required_permission
        return None
    return _role_name_to_rank(required_permission)


def _get_role_rank_map(conn) -> dict[int, int]:
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT Role_ID, RoleName FROM Roles")
        rows = cur.fetchall()
    finally:
        cur.close()

    rank_map: dict[int, int] = {}
    unresolved: list[int] = []
    for row in rows:
        role_id = row["Role_ID"]
        rank = _role_name_to_rank(row.get("RoleName"))
        if rank is None:
            unresolved.append(role_id)
            continue
        rank_map[role_id] = rank

    if unresolved:
        for offset, role_id in enumerate(sorted(unresolved), start=1):
            rank_map[role_id] = min(PERM_DEPT_VIEW, offset)

    return rank_map


def _fetch_user_affiliations(conn, user_id: int) -> tuple[set[int], set[str]]:
    dept_ids: set[int] = set()
    colleges: set[str] = set()

    candidate_queries = [
        """
        SELECT DISTINCT e.DeptID AS DeptID, d.College AS College
        FROM Users u
        LEFT JOIN Employees e ON e.Email = u.Email
        LEFT JOIN Departments_Subdivisions d ON d.DeptID = e.DeptID
        WHERE u.UserID = %s
        """,
        """
        SELECT DISTINCT e.DeptID AS DeptID, d.College AS College
        FROM Users u
        LEFT JOIN Employees e ON e.FullName = u.Name
        LEFT JOIN Departments_Subdivisions d ON d.DeptID = e.DeptID
        WHERE u.UserID = %s
        """,
        """
        SELECT DISTINCT e.DeptID AS DeptID, d.College AS College
        FROM Users u
        LEFT JOIN People p ON p.FullName = u.Name
        LEFT JOIN Employees e ON e.FullName = p.FullName
        LEFT JOIN Departments_Subdivisions d ON d.DeptID = e.DeptID
        WHERE u.UserID = %s
        """,
    ]

    for query in candidate_queries:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(query, (user_id,))
            rows = cur.fetchall()
        except Error:
            cur.close()
            continue
        finally:
            if hasattr(cur, "close"):
                cur.close()

        for row in rows:
            if row.get("DeptID") is not None:
                dept_ids.add(int(row["DeptID"]))
            if row.get("College"):
                colleges.add(str(row["College"]))

        if dept_ids or colleges:
            break

    return dept_ids, colleges


def _get_user_context(conn, user_id: int) -> dict[str, Any] | None:
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT u.UserID, u.Role_ID, r.RoleName
            FROM Users u
            JOIN Roles r ON r.Role_ID = u.Role_ID
            WHERE u.UserID = %s
            """,
            (user_id,),
        )
        user_row = cur.fetchone()
    finally:
        cur.close()

    if not user_row:
        return None

    rank_map = _get_role_rank_map(conn)
    rank = rank_map.get(user_row["Role_ID"])
    dept_ids, colleges = _fetch_user_affiliations(conn, user_id)

    return {
        "UserID": user_row["UserID"],
        "RoleID": user_row["Role_ID"],
        "RoleName": user_row["RoleName"],
        "Rank": rank,
        "DeptIDs": dept_ids,
        "Colleges": colleges,
    }


def _normalize_affiliation(affiliation: dict[str, Any] | None) -> dict[str, Any]:
    if not affiliation:
        return {}
    normalized: dict[str, Any] = {}
    if "department" in affiliation and affiliation["department"] not in (None, ""):
        departments = affiliation["department"]
        if not isinstance(departments, list):
            departments = [departments]
        normalized["department"] = [int(dept) for dept in departments]
    if "college" in affiliation and affiliation["college"] not in (None, ""):
        colleges = affiliation["college"]
        if isinstance(colleges, list):
            normalized["college"] = [str(c) for c in colleges]
        else:
            normalized["college"] = [str(colleges)]
    return normalized


def validatePermission(conn, required_permission: int | str, user_id: int, affiliation: dict[str, Any] | None) -> bool:
    required_rank = _resolve_required_rank(required_permission)
    if required_rank is None:
        return False

    context = _get_user_context(conn, user_id)
    if not context or context["Rank"] is None:
        return False

    user_rank = context["Rank"]
    if user_rank > required_rank:
        return False

    normalized_affiliation = _normalize_affiliation(affiliation)
    if not normalized_affiliation:
        return True

    if user_rank == PERM_GOD:
        return True

    user_colleges = context["Colleges"]
    user_depts = context["DeptIDs"]

    required_colleges = set(normalized_affiliation.get("college", []))
    if required_colleges:
        if not user_colleges or user_colleges.isdisjoint(required_colleges):
            return False

    required_depts = set(normalized_affiliation.get("department", []))
    if required_depts:
        if not user_depts or user_depts.isdisjoint(required_depts):
            return False

    return True


def _require_permission(conn, required_permission: int | str, user_id: int, affiliation: dict[str, Any] | None) -> None:
    if not validatePermission(conn, required_permission, user_id, affiliation):
        raise PermissionDeniedError("Permission denied")


def _resolve_college(conn, college_name: str) -> str | None:
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT AbbreviatedName, FullName
            FROM Colleges
            WHERE LOWER(AbbreviatedName) = LOWER(%s)
               OR LOWER(FullName) = LOWER(%s)
            LIMIT 1
            """,
            (college_name, college_name),
        )
        row = cur.fetchone()
    finally:
        cur.close()

    if not row:
        return None
    return row["AbbreviatedName"]


def _room_exists(conn, building_number: str, room_number: str) -> bool:
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT 1 FROM Rooms WHERE BuildingNumber = %s AND RoomNumber = %s LIMIT 1",
            (building_number, room_number),
        )
        return cur.fetchone() is not None
    finally:
        cur.close()


def _room_affiliation(conn, building_number: str, room_number: str) -> dict[str, Any]:
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT DISTINCT ra.DeptID, d.College
            FROM RoomsAreAssignedToDepts_Subdiv ra
            LEFT JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE ra.BuildingNumber = %s AND ra.RoomNumber = %s
            """,
            (building_number, room_number),
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    dept_ids = sorted({int(row["DeptID"]) for row in rows if row.get("DeptID") is not None})
    colleges = sorted({str(row["College"]) for row in rows if row.get("College")})

    affiliation: dict[str, Any] = {}
    if dept_ids:
        affiliation["department"] = dept_ids if len(dept_ids) > 1 else dept_ids[0]
    if len(colleges) == 1:
        affiliation["college"] = colleges[0]
    return affiliation


def _floor_affiliation(conn, building_number: str, floor_number: int) -> dict[str, Any]:
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT DISTINCT ra.DeptID, d.College
            FROM Rooms r
            LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra
              ON ra.BuildingNumber = r.BuildingNumber
             AND ra.RoomNumber = r.RoomNumber
            LEFT JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE r.BuildingNumber = %s AND r.FloorNumber = %s
            """,
            (building_number, floor_number),
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    dept_ids = sorted({int(row["DeptID"]) for row in rows if row.get("DeptID") is not None})
    colleges = sorted({str(row["College"]) for row in rows if row.get("College")})

    affiliation: dict[str, Any] = {}
    if dept_ids:
        affiliation["department"] = dept_ids if len(dept_ids) > 1 else dept_ids[0]
    if len(colleges) == 1:
        affiliation["college"] = colleges[0]
    return affiliation


def _department_row(conn, department_identifier: Any, college_name: str | None = None) -> dict[str, Any] | None:
    cur = conn.cursor(dictionary=True)
    try:
        if isinstance(department_identifier, int) or (
            isinstance(department_identifier, str) and department_identifier.isdigit()
        ):
            cur.execute(
                """
                SELECT DeptID, DepartmentName, College
                FROM Departments_Subdivisions
                WHERE DeptID = %s
                LIMIT 1
                """,
                (int(department_identifier),),
            )
            return cur.fetchone()

        if college_name:
            college_abbrev = _resolve_college(conn, college_name) or college_name
            cur.execute(
                """
                SELECT DeptID, DepartmentName, College
                FROM Departments_Subdivisions
                WHERE LOWER(DepartmentName) = LOWER(%s)
                  AND LOWER(College) = LOWER(%s)
                LIMIT 1
                """,
                (str(department_identifier), college_abbrev),
            )
        else:
            cur.execute(
                """
                SELECT DeptID, DepartmentName, College
                FROM Departments_Subdivisions
                WHERE LOWER(DepartmentName) = LOWER(%s)
                LIMIT 1
                """,
                (str(department_identifier),),
            )
        return cur.fetchone()
    finally:
        cur.close()


def _employee_row(conn, employee_identifier: Any) -> dict[str, Any] | None:
    emp_id = None
    email = None
    full_name = None
    department = None
    college = None

    if isinstance(employee_identifier, dict):
        emp_id = employee_identifier.get("emp_id") or employee_identifier.get("EmpID")
        email = employee_identifier.get("email") or employee_identifier.get("Email")
        full_name = employee_identifier.get("name") or employee_identifier.get("full_name") or employee_identifier.get("FullName")
        department = employee_identifier.get("department") or employee_identifier.get("Department")
        college = employee_identifier.get("college") or employee_identifier.get("College")
    elif isinstance(employee_identifier, int):
        emp_id = employee_identifier
    elif isinstance(employee_identifier, str):
        if "@" in employee_identifier:
            email = employee_identifier
        elif employee_identifier.isdigit():
            emp_id = int(employee_identifier)
        else:
            full_name = employee_identifier

    cur = conn.cursor(dictionary=True)
    try:
        base_query = """
            SELECT e.EmpID, e.Email, e.FullName, e.DeptID, d.DepartmentName, d.College
            FROM Employees e
            JOIN Departments_Subdivisions d ON d.DeptID = e.DeptID
        """
        if emp_id is not None:
            cur.execute(f"{base_query} WHERE e.EmpID = %s LIMIT 1", (int(emp_id),))
            return cur.fetchone()
        if email:
            cur.execute(f"{base_query} WHERE LOWER(e.Email) = LOWER(%s) LIMIT 1", (email,))
            return cur.fetchone()
        if full_name and department:
            query = f"""
                {base_query}
                WHERE LOWER(e.FullName) = LOWER(%s)
                  AND LOWER(d.DepartmentName) = LOWER(%s)
            """
            params: list[Any] = [full_name, department]
            if college:
                query += " AND LOWER(d.College) = LOWER(%s)"
                params.append(college)
            query += " LIMIT 1"
            cur.execute(query, tuple(params))
            return cur.fetchone()
        if full_name:
            cur.execute(
                f"{base_query} WHERE LOWER(e.FullName) = LOWER(%s) ORDER BY e.EmpID LIMIT 1",
                (full_name,),
            )
            return cur.fetchone()
        return None
    finally:
        cur.close()


def _equipment_row(conn, equipment_identifier: Any) -> dict[str, Any] | None:
    cur = conn.cursor(dictionary=True)
    try:
        if isinstance(equipment_identifier, int) or (
            isinstance(equipment_identifier, str) and str(equipment_identifier).isdigit()
        ):
            cur.execute(
                "SELECT EId, EType, IsSensitive FROM Equipment WHERE EId = %s LIMIT 1",
                (int(equipment_identifier),),
            )
            return cur.fetchone()

        cur.execute(
            "SELECT EId, EType, IsSensitive FROM Equipment WHERE LOWER(EType) = LOWER(%s) LIMIT 1",
            (str(equipment_identifier),),
        )
        return cur.fetchone()
    finally:
        cur.close()


def _filter_rows_by_scope(rows: list[dict[str, Any]], context: dict[str, Any]) -> list[dict[str, Any]]:
    rank = context["Rank"]
    if rank == PERM_GOD:
        return rows

    user_colleges = context["Colleges"]
    user_depts = context["DeptIDs"]
    filtered: list[dict[str, Any]] = []
    for row in rows:
        dept_id = row.get("DeptID")
        college = row.get("College")
        if rank in {PERM_COLLEGE_UPDATE, PERM_COLLEGE_VIEW}:
            if not college or college in user_colleges:
                filtered.append(row)
        elif rank in {PERM_DEPT_UPDATE, PERM_DEPT_VIEW}:
            if dept_id is None:
                continue
            if int(dept_id) in user_depts:
                filtered.append(row)
        else:
            filtered.append(row)
    return filtered


def _department_type(department_name: str) -> str:
    normalized = _normalize_text(department_name)
    academic_markers = ["science", "mathematics", "physics", "chemistry", "statistics", "biology", "kinesiology"]
    if any(marker in normalized for marker in academic_markers):
        return "Academic"
    return "Subdivision"


def _permission_error_code(conn, required_permission: int | str, user_id: int, affiliation: dict[str, Any] | None) -> str | None:
    if not validatePermission(conn, required_permission, user_id, affiliation):
        return ERR_UNAUTHORIZED
    return None


def getFloorplans(conn, user_id: int) -> list[dict[str, Any]]:
    _require_permission(conn, PERM_DEPT_VIEW, user_id, {})
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                fp.FileName AS URI,
                b.Name AS BuildingName,
                fp.BuildingNumber AS BuildingNumber,
                fp.FloorNumber AS FloorNumber
            FROM FloorPlans fp
            JOIN Buildings b ON b.BuildingNumber = fp.BuildingNumber
            ORDER BY fp.BuildingNumber, fp.FloorNumber, fp.FileName
            """
        )
        return cur.fetchall()
    finally:
        cur.close()


def getRooms(conn, user_id: int, building_number: str, floor_number: int) -> list[dict[str, Any]]:
    affiliation = _floor_affiliation(conn, building_number, floor_number)
    _require_permission(conn, PERM_DEPT_VIEW, user_id, affiliation)
    context = _get_user_context(conn, user_id)
    if not context:
        raise PermissionDeniedError("Invalid user context")

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                r.BuildingNumber,
                r.RoomNumber,
                rc.TopLeftX,
                rc.TopLeftY,
                rc.BottomRightX,
                rc.BottomRightY,
                ra.DeptID,
                d.College,
                d.DepartmentName
            FROM Rooms r
            LEFT JOIN RoomCoordinates rc
              ON rc.BuildingNumber = r.BuildingNumber
             AND rc.RoomNumber = r.RoomNumber
            LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra
              ON ra.BuildingNumber = r.BuildingNumber
             AND ra.RoomNumber = r.RoomNumber
            LEFT JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE r.BuildingNumber = %s
              AND r.FloorNumber = %s
            ORDER BY r.RoomNumber
            """,
            (building_number, floor_number),
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    rows = _filter_rows_by_scope(rows, context)
    for row in rows:
        row.pop("DeptID", None)
        row.pop("College", None)
    return rows


def findRoom(conn, user_id: int, building_number: str, floor_number: int, x: int, y: int) -> dict[str, Any] | None:
    affiliation = _floor_affiliation(conn, building_number, floor_number)
    _require_permission(conn, PERM_DEPT_VIEW, user_id, affiliation)
    context = _get_user_context(conn, user_id)
    if not context:
        raise PermissionDeniedError("Invalid user context")

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                r.BuildingNumber,
                r.RoomNumber,
                ra.DeptID,
                d.College,
                ABS(rc.BottomRightX - rc.TopLeftX) * ABS(rc.BottomRightY - rc.TopLeftY) AS RoomArea
            FROM Rooms r
            JOIN RoomCoordinates rc
              ON rc.BuildingNumber = r.BuildingNumber
             AND rc.RoomNumber = r.RoomNumber
            LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra
              ON ra.BuildingNumber = r.BuildingNumber
             AND ra.RoomNumber = r.RoomNumber
            LEFT JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE r.BuildingNumber = %s
              AND r.FloorNumber = %s
              AND %s BETWEEN rc.TopLeftX AND rc.BottomRightX
              AND %s BETWEEN rc.TopLeftY AND rc.BottomRightY
            ORDER BY RoomArea ASC, r.RoomNumber ASC
            """,
            (building_number, floor_number, x, y),
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    rows = _filter_rows_by_scope(rows, context)
    if not rows:
        return None
    return {"BuildingNumber": rows[0]["BuildingNumber"], "RoomNumber": rows[0]["RoomNumber"]}


def getRoomInfo(conn, user_id: int, building_number: str, room_number: str) -> dict[str, Any]:
    affiliation = _room_affiliation(conn, building_number, room_number)
    _require_permission(conn, PERM_DEPT_VIEW, user_id, affiliation)
    context = _get_user_context(conn, user_id)
    if not context:
        raise PermissionDeniedError("Invalid user context")

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                r.BuildingNumber,
                r.RoomNumber,
                r.FloorNumber,
                r.RoomUseCode,
                r.SpaceCode,
                r.FurnitureCode,
                r.SquareFeet,
                r.Notes,
                rc.TopLeftX,
                rc.TopLeftY,
                rc.BottomRightX,
                rc.BottomRightY,
                ra.DeptID,
                d.College,
                d.DepartmentName
            FROM Rooms r
            LEFT JOIN RoomCoordinates rc
              ON rc.BuildingNumber = r.BuildingNumber
             AND rc.RoomNumber = r.RoomNumber
            LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra
              ON ra.BuildingNumber = r.BuildingNumber
             AND ra.RoomNumber = r.RoomNumber
            LEFT JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE r.BuildingNumber = %s
              AND r.RoomNumber = %s
            LIMIT 1
            """,
            (building_number, room_number),
        )
        room = cur.fetchone()
        if not room:
            raise NotFoundError("Room not found")

        if not _filter_rows_by_scope([room], context):
            raise PermissionDeniedError("Permission denied for room scope")

        cur.execute(
            """
            SELECT
                e.EmpID,
                e.FullName,
                e.Email,
                p.PhoneNumber
            FROM EmployeesAssignedToRooms ear
            JOIN Employees e ON e.EmpID = ear.EmpID
            LEFT JOIN People p ON p.FullName = e.FullName
            WHERE ear.BuildingNumber = %s
              AND ear.RoomNumber = %s
            ORDER BY e.FullName
            """,
            (building_number, room_number),
        )
        people_rows = cur.fetchall()

        cur.execute(
            """
            SELECT
                eq.EId,
                eq.EType,
                eq.IsSensitive,
                rew.Quantity
            FROM RoomsAreEquippedWithEquipment rew
            JOIN Equipment eq ON eq.EId = rew.EId
            WHERE rew.BuildingNumber = %s
              AND rew.RoomNumber = %s
            ORDER BY eq.EType
            """,
            (building_number, room_number),
        )
        equipment_rows = cur.fetchall()
    finally:
        cur.close()

    return {
        "BuildingNumber": room["BuildingNumber"],
        "RoomNumber": room["RoomNumber"],
        "FloorNumber": room["FloorNumber"],
        "RoomUseCode": room["RoomUseCode"],
        "SpaceCode": room["SpaceCode"],
        "FurnitureCode": room["FurnitureCode"],
        "SquareFeet": _to_float(room["SquareFeet"]),
        "Notes": room["Notes"],
        "BoundingBox": {
            "TopLeftX": room["TopLeftX"],
            "TopLeftY": room["TopLeftY"],
            "BottomRightX": room["BottomRightX"],
            "BottomRightY": room["BottomRightY"],
        },
        "Department": {
            "DeptID": room["DeptID"],
            "DepartmentName": room["DepartmentName"],
            "College": room["College"],
        },
        "People": [
            {
                "EmpID": p["EmpID"],
                "FullName": p["FullName"],
                "Email": p["Email"],
                "Position": None,
                "Phone": p["PhoneNumber"],
            }
            for p in people_rows
        ],
        "Equipment": [
            {
                "EId": e["EId"],
                "EType": e["EType"],
                "IsSensitive": int(e["IsSensitive"]),
                "Quantity": int(e["Quantity"]),
            }
            for e in equipment_rows
        ],
    }


def getDeptList(conn, user_id: int, college_name: str) -> list[dict[str, Any]]:
    college = _resolve_college(conn, college_name)
    if not college:
        raise NotFoundError("College not found")

    _require_permission(conn, PERM_DEPT_VIEW, user_id, {"college": college})
    context = _get_user_context(conn, user_id)
    if not context:
        raise PermissionDeniedError("Invalid user context")

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                d.DeptID,
                d.DepartmentName,
                d.College,
                MIN(CONCAT(ra.BuildingNumber, '-', ra.RoomNumber)) AS MainOfficeLocation
            FROM Departments_Subdivisions d
            LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra ON ra.DeptID = d.DeptID
            WHERE d.College = %s
            GROUP BY d.DeptID, d.DepartmentName, d.College
            ORDER BY d.DepartmentName
            """,
            (college,),
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    rows = _filter_rows_by_scope(rows, context)
    output = []
    for row in rows:
        output.append(
            {
                "DepartmentName": row["DepartmentName"],
                "MainOfficeLocation": row["MainOfficeLocation"],
                "DepartmentHead": None,
                "DepartmentType": _department_type(row["DepartmentName"]),
            }
        )
    return output


def getEmployees(conn, user_id: int, college_name: str, department_name: str) -> list[dict[str, Any]]:
    dept = _department_row(conn, department_name, college_name)
    if not dept:
        raise NotFoundError("Department not found")

    affiliation = {"department": dept["DeptID"], "college": dept["College"]}
    _require_permission(conn, PERM_DEPT_VIEW, user_id, affiliation)

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                e.EmpID,
                e.FullName,
                e.Email,
                e.DeptID,
                d.DepartmentName,
                d.College,
                p.PhoneNumber
            FROM Employees e
            JOIN Departments_Subdivisions d ON d.DeptID = e.DeptID
            LEFT JOIN People p ON p.FullName = e.FullName
            WHERE e.DeptID = %s
            ORDER BY e.FullName, e.EmpID
            """,
            (dept["DeptID"],),
        )
        employee_rows = cur.fetchall()

        cur.execute(
            """
            WITH OccupantCounts AS (
                SELECT BuildingNumber, RoomNumber, COUNT(*) AS OccupantCount
                FROM EmployeesAssignedToRooms
                GROUP BY BuildingNumber, RoomNumber
            )
            SELECT
                ear.EmpID,
                r.BuildingNumber,
                r.RoomNumber,
                r.RoomUseCode,
                r.SquareFeet,
                oc.OccupantCount,
                CASE
                    WHEN oc.OccupantCount > 0 THEN r.SquareFeet / oc.OccupantCount
                    ELSE NULL
                END AS EmployeeShareSquareFeet
            FROM EmployeesAssignedToRooms ear
            JOIN Employees e ON e.EmpID = ear.EmpID
            JOIN Rooms r
              ON r.BuildingNumber = ear.BuildingNumber
             AND r.RoomNumber = ear.RoomNumber
            LEFT JOIN OccupantCounts oc
              ON oc.BuildingNumber = ear.BuildingNumber
             AND oc.RoomNumber = ear.RoomNumber
            WHERE e.DeptID = %s
            ORDER BY ear.EmpID, r.BuildingNumber, r.RoomNumber
            """,
            (dept["DeptID"],),
        )
        share_rows = cur.fetchall()
    finally:
        cur.close()

    employees: dict[int, dict[str, Any]] = {}
    for row in employee_rows:
        employees[row["EmpID"]] = {
            "EmpID": row["EmpID"],
            "FullName": row["FullName"],
            "Email": row["Email"],
            "Position": None,
            "Phone": row["PhoneNumber"],
            "Department": row["DepartmentName"],
            "College": row["College"],
            "Rooms": [],
            "TotalSpaceSquareFeet": 0.0,
        }

    for row in share_rows:
        emp = employees.get(row["EmpID"])
        if not emp:
            continue
        share = _to_float(row["EmployeeShareSquareFeet"]) or 0.0
        emp["Rooms"].append(
            {
                "BuildingNumber": row["BuildingNumber"],
                "RoomNumber": row["RoomNumber"],
                "RoomUseCode": row["RoomUseCode"],
                "SquareFeet": _to_float(row["SquareFeet"]),
                "EmployeeShareSquareFeet": share,
            }
        )
        emp["TotalSpaceSquareFeet"] += share

    return list(employees.values())


def getEmployeeInfo(conn, user_id: int, employee_identifier: Any) -> dict[str, Any]:
    employee = _employee_row(conn, employee_identifier)
    if not employee:
        raise NotFoundError("Employee not found")

    affiliation = {"department": employee["DeptID"], "college": employee["College"]}
    _require_permission(conn, PERM_DEPT_VIEW, user_id, affiliation)

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            WITH OccupantCounts AS (
                SELECT BuildingNumber, RoomNumber, COUNT(*) AS OccupantCount
                FROM EmployeesAssignedToRooms
                GROUP BY BuildingNumber, RoomNumber
            )
            SELECT
                r.BuildingNumber,
                r.RoomNumber,
                r.RoomUseCode,
                r.SquareFeet,
                oc.OccupantCount,
                CASE
                    WHEN oc.OccupantCount > 0 THEN r.SquareFeet / oc.OccupantCount
                    ELSE NULL
                END AS EmployeeShareSquareFeet
            FROM EmployeesAssignedToRooms ear
            JOIN Rooms r
              ON r.BuildingNumber = ear.BuildingNumber
             AND r.RoomNumber = ear.RoomNumber
            LEFT JOIN OccupantCounts oc
              ON oc.BuildingNumber = ear.BuildingNumber
             AND oc.RoomNumber = ear.RoomNumber
            WHERE ear.EmpID = %s
            ORDER BY r.BuildingNumber, r.RoomNumber
            """,
            (employee["EmpID"],),
        )
        rooms = cur.fetchall()
    finally:
        cur.close()

    total_share = 0.0
    normalized_rooms: list[dict[str, Any]] = []
    for row in rooms:
        share = _to_float(row["EmployeeShareSquareFeet"]) or 0.0
        total_share += share
        normalized_rooms.append(
            {
                "BuildingNumber": row["BuildingNumber"],
                "RoomNumber": row["RoomNumber"],
                "RoomUseCode": row["RoomUseCode"],
                "SquareFeet": _to_float(row["SquareFeet"]),
                "EmployeeShareSquareFeet": share,
            }
        )

    return {
        "EmpID": employee["EmpID"],
        "FullName": employee["FullName"],
        "Email": employee["Email"],
        "Position": None,
        "Department": employee["DepartmentName"],
        "College": employee["College"],
        "Rooms": normalized_rooms,
        "TotalSpaceSquareFeet": total_share,
    }


def getEquipmentLocations(conn, user_id: int, equipment_identifier: Any) -> list[dict[str, Any]]:
    equipment = _equipment_row(conn, equipment_identifier)
    if not equipment:
        raise NotFoundError("Equipment type not found")

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT DISTINCT ra.DeptID, d.College
            FROM RoomsAreEquippedWithEquipment rew
            LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra
              ON ra.BuildingNumber = rew.BuildingNumber
             AND ra.RoomNumber = rew.RoomNumber
            LEFT JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE rew.EId = %s
            """,
            (equipment["EId"],),
        )
        aff_rows = cur.fetchall()
    finally:
        cur.close()

    dept_ids = sorted({int(row["DeptID"]) for row in aff_rows if row.get("DeptID") is not None})
    colleges = sorted({str(row["College"]) for row in aff_rows if row.get("College")})
    affiliation: dict[str, Any] = {}
    if dept_ids:
        affiliation["department"] = dept_ids
    if len(colleges) == 1:
        affiliation["college"] = colleges[0]

    _require_permission(conn, PERM_DEPT_VIEW, user_id, affiliation)
    context = _get_user_context(conn, user_id)
    if not context:
        raise PermissionDeniedError("Invalid user context")

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                rew.BuildingNumber,
                rew.RoomNumber,
                rew.Quantity,
                ra.DeptID,
                d.College
            FROM RoomsAreEquippedWithEquipment rew
            LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra
              ON ra.BuildingNumber = rew.BuildingNumber
             AND ra.RoomNumber = rew.RoomNumber
            LEFT JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE rew.EId = %s
            ORDER BY rew.BuildingNumber, rew.RoomNumber
            """,
            (equipment["EId"],),
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    rows = _filter_rows_by_scope(rows, context)
    return [
        {
            "BuildingNumber": row["BuildingNumber"],
            "RoomNumber": row["RoomNumber"],
            "Quantity": int(row["Quantity"]),
        }
        for row in rows
    ]


def getSensitiveEquipmentLocations(conn, user_id: int, college_name: str) -> list[dict[str, Any]]:
    college = _resolve_college(conn, college_name)
    if not college:
        raise NotFoundError("College not found")

    _require_permission(conn, PERM_DEPT_VIEW, user_id, {"college": college})
    context = _get_user_context(conn, user_id)
    if not context:
        raise PermissionDeniedError("Invalid user context")

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                rew.BuildingNumber,
                rew.RoomNumber,
                eq.EId,
                eq.EType,
                rew.Quantity,
                ra.DeptID,
                d.College
            FROM RoomsAreEquippedWithEquipment rew
            JOIN Equipment eq ON eq.EId = rew.EId
            LEFT JOIN RoomsAreAssignedToDepts_Subdiv ra
              ON ra.BuildingNumber = rew.BuildingNumber
             AND ra.RoomNumber = rew.RoomNumber
            LEFT JOIN Departments_Subdivisions d ON d.DeptID = ra.DeptID
            WHERE eq.IsSensitive = 1
              AND d.College = %s
            ORDER BY rew.BuildingNumber, rew.RoomNumber, eq.EType
            """,
            (college,),
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    rows = _filter_rows_by_scope(rows, context)
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["BuildingNumber"], row["RoomNumber"])
        if key not in grouped:
            grouped[key] = {
                "BuildingNumber": row["BuildingNumber"],
                "RoomNumber": row["RoomNumber"],
                "Equipment": [],
            }
        grouped[key]["Equipment"].append(
            {
                "EId": row["EId"],
                "EType": row["EType"],
                "Quantity": int(row["Quantity"]),
            }
        )
    return list(grouped.values())


def logLogin(conn, user_id: int, commit: bool = True) -> str:
    if _permission_error_code(conn, PERM_DEPT_VIEW, user_id, {}) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Logs (UserID) VALUES (%s)", (user_id,))
        if commit:
            conn.commit()
        return SUCCESS
    except Error:
        conn.rollback()
        return ERR_LOGGING_FAILURE
    finally:
        cur.close()


def logLogout(conn, user_id: int, commit: bool = True) -> str:
    if _permission_error_code(conn, PERM_DEPT_VIEW, user_id, {}) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Logs (UserID, LogOut) VALUES (%s, CURTIME())", (user_id,))
        if commit:
            conn.commit()
        return SUCCESS
    except Error:
        conn.rollback()
        return ERR_LOGGING_FAILURE
    finally:
        cur.close()


def logRoomAssignmentPerson(
    conn,
    user_id: int,
    building_number: str,
    room_number: str,
    employee_id: int,
    action_type: str,
    commit: bool = True,
) -> str:
    affiliation = _room_affiliation(conn, building_number, room_number)
    if _permission_error_code(conn, PERM_DEPT_UPDATE, user_id, affiliation) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    action = "Assign" if _normalize_text(action_type).startswith("assign") else "Delete"
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Logs (UserID, AssignOrDelete, BuildingNumber, RoomNumber, EmpID)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, action, building_number, room_number, employee_id),
        )
        if commit:
            conn.commit()
        return SUCCESS
    except Error:
        conn.rollback()
        return ERR_LOGGING_FAILURE
    finally:
        cur.close()


def logEquipmentAssignment(
    conn,
    user_id: int,
    building_number: str,
    room_number: str,
    equipment_id: int,
    before_count: int,
    after_count: int,
    commit: bool = True,
) -> str:
    affiliation = _room_affiliation(conn, building_number, room_number)
    if _permission_error_code(conn, PERM_DEPT_UPDATE, user_id, affiliation) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    action = "Delete" if after_count == 0 else "Assign"
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Logs (UserID, AssignOrDelete, BuildingNumber, RoomNumber, EId, Quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, action, building_number, room_number, equipment_id, after_count),
        )
        if commit:
            conn.commit()
        return SUCCESS
    except Error:
        conn.rollback()
        return ERR_LOGGING_FAILURE
    finally:
        cur.close()


def logRoomDeptChange(
    conn,
    user_id: int,
    building_number: str,
    room_number: str,
    from_dept: int | None,
    to_dept: int | None,
    commit: bool = True,
) -> str:
    affiliation = _room_affiliation(conn, building_number, room_number)
    if to_dept is not None:
        dept_row = _department_row(conn, to_dept)
        if dept_row:
            affiliation = {"department": dept_row["DeptID"], "college": dept_row["College"]}

    if _permission_error_code(conn, PERM_DEPT_UPDATE, user_id, affiliation) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    action = "Assign" if to_dept is not None else "Delete"
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Logs (UserID, AssignOrDelete, BuildingNumber, RoomNumber, DeptID)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, action, building_number, room_number, to_dept),
        )
        if commit:
            conn.commit()
        return SUCCESS
    except Error:
        conn.rollback()
        return ERR_LOGGING_FAILURE
    finally:
        cur.close()


def addEmployee(
    conn,
    user_id: int,
    full_name: str,
    email: str,
    dept_id: int,
    position: str | None = None,
    phone: str | None = None,
) -> str:
    dept = _department_row(conn, dept_id)
    if not dept:
        return ERR_NOT_FOUND

    affiliation = {"department": dept["DeptID"], "college": dept["College"]}
    if _permission_error_code(conn, PERM_DEPT_UPDATE, user_id, affiliation) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Employees (Email, FullName, DeptID) VALUES (%s, %s, %s)",
            (email, full_name, dept["DeptID"]),
        )
        if phone:
            cur.execute(
                """
                INSERT INTO People (FullName, PhoneNumber)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE PhoneNumber = VALUES(PhoneNumber)
                """,
                (full_name, phone),
            )
        conn.commit()
        return SUCCESS
    except IntegrityError as exc:
        conn.rollback()
        return _map_mysql_error(exc)
    except Error:
        conn.rollback()
        return ERR_TYPE_MISMATCH
    finally:
        cur.close()


def assignRoom(conn, user_id: int, employee_identifier: Any, building_number: str, room_number: str) -> str:
    employee = _employee_row(conn, employee_identifier)
    if not employee:
        return ERR_NOT_FOUND
    if not _room_exists(conn, building_number, room_number):
        return ERR_NOT_FOUND

    affiliation = _room_affiliation(conn, building_number, room_number)
    if not affiliation:
        affiliation = {"department": employee["DeptID"], "college": employee["College"]}
    if _permission_error_code(conn, PERM_DEPT_UPDATE, user_id, affiliation) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT 1
            FROM EmployeesAssignedToRooms
            WHERE EmpID = %s AND BuildingNumber = %s AND RoomNumber = %s
            LIMIT 1
            """,
            (employee["EmpID"], building_number, room_number),
        )
        if cur.fetchone():
            return ERR_DUPLICATE

        log_result = logRoomAssignmentPerson(
            conn,
            user_id,
            building_number,
            room_number,
            employee["EmpID"],
            "Assign",
            commit=False,
        )
        if log_result != SUCCESS:
            conn.rollback()
            return ERR_LOGGING_FAILURE if log_result != ERR_UNAUTHORIZED else ERR_UNAUTHORIZED

        cur.execute(
            """
            INSERT INTO EmployeesAssignedToRooms (EmpID, RoomNumber, BuildingNumber)
            VALUES (%s, %s, %s)
            """,
            (employee["EmpID"], room_number, building_number),
        )
        conn.commit()
        return SUCCESS
    except IntegrityError as exc:
        conn.rollback()
        return _map_mysql_error(exc)
    except Error:
        conn.rollback()
        return ERR_TYPE_MISMATCH
    finally:
        cur.close()


def removeRoomAssignment(conn, user_id: int, employee_identifier: Any, building_number: str, room_number: str) -> str:
    employee = _employee_row(conn, employee_identifier)
    if not employee:
        return ERR_NOT_FOUND
    if not _room_exists(conn, building_number, room_number):
        return ERR_NOT_FOUND

    affiliation = _room_affiliation(conn, building_number, room_number)
    if not affiliation:
        affiliation = {"department": employee["DeptID"], "college": employee["College"]}
    if _permission_error_code(conn, PERM_DEPT_UPDATE, user_id, affiliation) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT 1
            FROM EmployeesAssignedToRooms
            WHERE EmpID = %s AND BuildingNumber = %s AND RoomNumber = %s
            LIMIT 1
            """,
            (employee["EmpID"], building_number, room_number),
        )
        if not cur.fetchone():
            return ERR_NOT_FOUND

        log_result = logRoomAssignmentPerson(
            conn,
            user_id,
            building_number,
            room_number,
            employee["EmpID"],
            "Delete",
            commit=False,
        )
        if log_result != SUCCESS:
            conn.rollback()
            return ERR_LOGGING_FAILURE if log_result != ERR_UNAUTHORIZED else ERR_UNAUTHORIZED

        cur.execute(
            """
            DELETE FROM EmployeesAssignedToRooms
            WHERE EmpID = %s AND BuildingNumber = %s AND RoomNumber = %s
            """,
            (employee["EmpID"], building_number, room_number),
        )
        conn.commit()
        return SUCCESS
    except Error:
        conn.rollback()
        return ERR_TYPE_MISMATCH
    finally:
        cur.close()


def departmentAssignment(conn, user_id: int, dept_identifier: Any, building_number: str, room_number: str) -> str:
    dept = _department_row(conn, dept_identifier)
    if not dept:
        return ERR_NOT_FOUND
    if not _room_exists(conn, building_number, room_number):
        return ERR_NOT_FOUND

    affiliation = {"department": dept["DeptID"], "college": dept["College"]}
    if _permission_error_code(conn, PERM_DEPT_UPDATE, user_id, affiliation) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT DeptID
            FROM RoomsAreAssignedToDepts_Subdiv
            WHERE BuildingNumber = %s AND RoomNumber = %s
            ORDER BY DeptID
            """,
            (building_number, room_number),
        )
        existing_rows = cur.fetchall()
        existing_depts = [int(row["DeptID"]) for row in existing_rows]
        from_dept = existing_depts[0] if existing_depts else None

        if existing_depts == [int(dept["DeptID"])]:
            return SUCCESS

        log_result = logRoomDeptChange(
            conn,
            user_id,
            building_number,
            room_number,
            from_dept=from_dept,
            to_dept=int(dept["DeptID"]),
            commit=False,
        )
        if log_result != SUCCESS:
            conn.rollback()
            return ERR_LOGGING_FAILURE if log_result != ERR_UNAUTHORIZED else ERR_UNAUTHORIZED

        cur.execute(
            """
            DELETE FROM RoomsAreAssignedToDepts_Subdiv
            WHERE BuildingNumber = %s AND RoomNumber = %s
            """,
            (building_number, room_number),
        )
        cur.execute(
            """
            INSERT INTO RoomsAreAssignedToDepts_Subdiv (BuildingNumber, RoomNumber, DeptID)
            VALUES (%s, %s, %s)
            """,
            (building_number, room_number, int(dept["DeptID"])),
        )
        conn.commit()
        return SUCCESS
    except IntegrityError as exc:
        conn.rollback()
        return _map_mysql_error(exc)
    except Error:
        conn.rollback()
        return ERR_TYPE_MISMATCH
    finally:
        cur.close()


def assignEquipment(
    conn,
    user_id: int,
    building_number: str,
    room_number: str,
    equipment_identifier: Any,
    new_count: int,
) -> str:
    if not isinstance(new_count, int) or new_count < 0:
        return ERR_TYPE_MISMATCH
    if not _room_exists(conn, building_number, room_number):
        return ERR_NOT_FOUND

    equipment = _equipment_row(conn, equipment_identifier)
    if not equipment:
        return ERR_NOT_FOUND

    affiliation = _room_affiliation(conn, building_number, room_number)
    if _permission_error_code(conn, PERM_DEPT_UPDATE, user_id, affiliation) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT Quantity
            FROM RoomsAreEquippedWithEquipment
            WHERE BuildingNumber = %s AND RoomNumber = %s AND EId = %s
            LIMIT 1
            """,
            (building_number, room_number, equipment["EId"]),
        )
        existing = cur.fetchone()
        before = int(existing["Quantity"]) if existing else 0
        after = int(new_count)

        if before == after:
            return SUCCESS

        log_result = logEquipmentAssignment(
            conn,
            user_id,
            building_number,
            room_number,
            equipment_id=int(equipment["EId"]),
            before_count=before,
            after_count=after,
            commit=False,
        )
        if log_result != SUCCESS:
            conn.rollback()
            return ERR_LOGGING_FAILURE if log_result != ERR_UNAUTHORIZED else ERR_UNAUTHORIZED

        if after == 0:
            cur.execute(
                """
                DELETE FROM RoomsAreEquippedWithEquipment
                WHERE BuildingNumber = %s AND RoomNumber = %s AND EId = %s
                """,
                (building_number, room_number, equipment["EId"]),
            )
        elif before == 0:
            cur.execute(
                """
                INSERT INTO RoomsAreEquippedWithEquipment
                    (BuildingNumber, RoomNumber, EId, Quantity)
                VALUES (%s, %s, %s, %s)
                """,
                (building_number, room_number, equipment["EId"], after),
            )
        else:
            cur.execute(
                """
                UPDATE RoomsAreEquippedWithEquipment
                SET Quantity = %s
                WHERE BuildingNumber = %s AND RoomNumber = %s AND EId = %s
                """,
                (after, building_number, room_number, equipment["EId"]),
            )

        conn.commit()
        return SUCCESS
    except IntegrityError as exc:
        conn.rollback()
        return _map_mysql_error(exc)
    except Error:
        conn.rollback()
        return ERR_TYPE_MISMATCH
    finally:
        cur.close()


def addEquipmentType(conn, user_id: int, equipment_type: str, is_sensitive: bool, description: str = "") -> str:
    if _permission_error_code(conn, PERM_COLLEGE_UPDATE, user_id, {}) == ERR_UNAUTHORIZED:
        return ERR_UNAUTHORIZED

    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Equipment (EType, EDescription, IsSensitive)
            VALUES (%s, %s, %s)
            """,
            (equipment_type, description or "", 1 if bool(is_sensitive) else 0),
        )
        conn.commit()
        return SUCCESS
    except IntegrityError as exc:
        conn.rollback()
        return _map_mysql_error(exc)
    except Error:
        conn.rollback()
        return ERR_TYPE_MISMATCH
    finally:
        cur.close()
