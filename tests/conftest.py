# pip install pytest httpx

import pytest
from fastapi.testclient import TestClient

import api.main as api

class FakeCursor:
    """
    A cursor that returns scripted rows based on which SQL is executed.
    """
    def __init__(self, script: dict):
        self.script = script
        self.last_query = ""
        self.last_params = None

    def execute(self, query: str, params=None):
        self.last_query = query
        self.last_params = params
        print("SQL:", query)
        print("PARAMS:", params)

    def fetchone(self):
        q = self.last_query

        # validatePermission query
        if "FROM Users u" in q and "LEFT JOIN Employees e" in q and "WHERE u.UserID = %s" in q:
            return self.script.get("validatePermission_row")

        # /getRoomInfo first query
        if "FROM Rooms r" in q and "JOIN RoomsAreAssignedToDepts_Subdiv" in q:
            return self.script.get("RoomInfo_row")

        return None

    def fetchall(self):
        q = self.last_query

       # /getEmployees room shares (rooms_query)
        if "WITH occupants AS" in q and "employee_share" in q:
            return self.script.get("EmployeeRoomShare_rows", [])

        # /getRoomInfo employees list
        if "FROM Employees e" in q and "EmployeesAssignedToRooms" in q:
            return self.script.get("RoomEmployees_rows", [])

        # /getRoomInfo equipment list
        if "FROM Equipment eq" in q and "RoomsAreEquippedWithEquipment" in q:
            return self.script.get("RoomEquip_rows", [])

        # /findRoom
        if "WITH getRooms AS" in q and "ORDER BY RoomArea" in q:
            return self.script.get("findRoom_rows", [])

        # /getRooms
        if "FROM Rooms r" in q and "JOIN RoomCoordinates" in q and "Departments_Subdivisions" in q:
            return self.script.get("getRooms_rows", [])

        # /getFloorplans
        if "FROM FloorPlans" in q and "JOIN Buildings" in q:
            return self.script.get("getFloorplans_rows", [])
        
        # /getEmployees employee list
        if "FROM Employees e" in q and "JOIN Departments_Subdivisions" in q and "WHERE d.College" in q:
            return self.script.get("Employees_rows", [])


        return []

    def close(self):
        pass


class FakeConn:
    def __init__(self, script: dict):
        self.script = script

    def cursor(self, dictionary: bool = False):
        return FakeCursor(self.script)

    def close(self):
        pass


@pytest.fixture
def script_ok():
    """
    Default DB script for a 'happy path' user and endpoints.
    Adjust values to match your schema expectations.
    """
    return {
        # validatePermission_row must include RoleID, DeptID, College (per your code)
        "validatePermission_row": {"RoleID": 5, "DeptID": 115100, "College": "BCSM"},

        # getRoomInfo: room record from Rooms + DepartmentName
        "RoomInfo_row": {
            "BuildingNumber": "033-0",
            "RoomNumber": "0351-00",
            "FloorNumber": 3,
            "RoomUseCode": 210,
            "SpaceCode": 2,
            "FurnitureCode": "03",
            "SquareFeet": 984.55,
            "Notes": "",
            "DepartmentName": "Biological Sciences",
        },
        "RoomEmployees_rows": [{}],
        "RoomEquip_rows": [{}],
        "findRoom_rows": [{"BuildingNumber": "033-0", "RoomNumber": "0351-00"}],
        "getRooms_rows": [{
            "BuildingNumber": "033-0",
            "RoomNumber": "0351-00",
            "TopLeftX": 197, "TopLeftY": 276, "BottomRightX": 248, "BottomRightY": 343,
            "DepartmentName": "Biological Sciences"
        }],
        "getFloorplans_rows": [{
            "URI": "building-033-Floor3.svg",
            "BuildingName": "Clyde P. Fisher Science Hall",
            "BuildingNumber": "033-0",
            "FloorNumber": 3,
        }],
        "Employees_rows": [
            {"EmpID": 1, "FullName": "Alice Example", "Email": "alice@calpoly.edu", "Position": "Professor", "Phone": "805-0101"},
        ],
        "EmployeeRoomShare_rows": [{
        
            "EmpID": 1,
            "BuildingNumber": "033-0",
            "RoomNumber": "100-00",
            "SquareFeet": 300.0,
            "occupant_count": 1,
            "employee_share": 300.0,
        }],
    }


@pytest.fixture
def monkeypatch_db(monkeypatch, script_ok):
    """
    Patch main.get_connection() + main.test_connection() to use our fake DB.
    """
    monkeypatch.setattr(api, "get_connection", lambda: FakeConn(script_ok))
    monkeypatch.setattr(api, "test_connection", lambda: True)
    return script_ok


@pytest.fixture
def client(monkeypatch_db):
    return TestClient(api.app)