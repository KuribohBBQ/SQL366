import api.lab4_api as lab4
from api.errors import ERR_UNAUTHORIZED, SUCCESS


def test_assign_equipment_write_ahead_logging(monkeypatch, fake_conn, events):
    monkeypatch.setattr(lab4, "_room_exists", lambda conn, b, r: True)
    monkeypatch.setattr(lab4, "_equipment_row", lambda conn, ident: {"EId": 23, "EType": "Refrigerator", "IsSensitive": 1})
    monkeypatch.setattr(lab4, "_room_affiliation", lambda conn, b, r: {"department": 115100, "college": "BCSM"})
    monkeypatch.setattr(lab4, "validatePermission", lambda conn, required, user, affiliation: True)

    def fake_log(conn, user_id, building_number, room_number, equipment_id, before_count, after_count, commit=False):
        events.append("log")
        return SUCCESS

    monkeypatch.setattr(lab4, "logEquipmentAssignment", fake_log)

    code = lab4.assignEquipment(
        fake_conn,
        user_id=1,
        building_number="033-0",
        room_number="0351-00",
        equipment_identifier=23,
        new_count=3,
    )

    assert code == SUCCESS
    assert events.index("log") < events.index("update")
    assert fake_conn.committed is True


def test_add_equipment_type_permission_denied(monkeypatch, fake_conn):
    monkeypatch.setattr(lab4, "validatePermission", lambda conn, required, user, affiliation: False)
    code = lab4.addEquipmentType(fake_conn, user_id=5, equipment_type="TMP", is_sensitive=False)
    assert code == ERR_UNAUTHORIZED


def test_validate_permission_from_role_name(monkeypatch):
    monkeypatch.setattr(
        lab4,
        "_get_user_context",
        lambda conn, user_id: {
            "UserID": user_id,
            "RoleID": 2,
            "RoleName": "College Update Level",
            "Rank": 2,
            "DeptIDs": {115100},
            "Colleges": {"BCSM"},
        },
    )

    assert lab4.validatePermission(object(), "Department View Level", user_id=2, affiliation={"college": "BCSM"}) is True
