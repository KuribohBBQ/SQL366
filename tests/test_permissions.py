import api.main as api

def test_validate_permission_pass(monkeypatch_db):
    assert api.validatePermission(5, userId=1, affiliation={}) is True

def test_validate_permission_fail_role(monkeypatch_db):
    assert api.validatePermission(2, userId=1, affiliation={}) is False

def test_get_room_info(monkeypatch_db):
    room_info = api.getRoomInfo("033-0", "0351-00")
    assert room_info is not None
    assert room_info["DepartmentName"] == "Biological Sciences"
    assert room_info["SquareFeet"] == 984.55
    assert room_info["RoomUseCode"] == 210
    assert room_info["FurnitureCode"] == "03"
    assert room_info["SpaceCode"] == 2
    assert room_info["Notes"] == ""
    assert room_info["FloorNumber"] == 3

