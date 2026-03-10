import api.lab4_api as lab4


def test_validate_permission_role_order_and_affiliation(monkeypatch):
    monkeypatch.setattr(
        lab4,
        "_get_user_context",
        lambda conn, user_id: {
            "UserID": user_id,
            "RoleID": 3,
            "RoleName": "Department Update Level",
            "Rank": 3,
            "DeptIDs": {115100},
            "Colleges": {"BCSM"},
        },
    )

    assert lab4.validatePermission(object(), "Department View Level", 7, {"department": 115100, "college": "BCSM"}) is True
    assert lab4.validatePermission(object(), "College Update Level", 7, {"college": "BCSM"}) is False
    assert lab4.validatePermission(object(), "Department View Level", 7, {"department": 999999, "college": "BCSM"}) is False


def test_get_floorplans_raises_when_permission_denied(monkeypatch):
    monkeypatch.setattr(lab4, "validatePermission", lambda conn, required_permission, user_id, affiliation: False)

    try:
        lab4.getFloorplans(object(), user_id=1)
        assert False, "Expected PermissionDeniedError"
    except lab4.PermissionDeniedError:
        assert True
