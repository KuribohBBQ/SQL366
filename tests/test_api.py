def test_getEmployees_returns_employee_and_square_feet(client):
    resp = client.get(
        "/getEmployees",
        params={
            "userId": 1,
            "college": "BCSM",
            "department": "Biological Sciences",
        },
    )

    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1

    employee = data[0]

    assert employee["FullName"] == "Alice Example"
    assert employee["Email"] == "alice@calpoly.edu"
    # assert employee["Position"] == "Professor"

    # check square footage calculation
    assert abs(float(employee["TotalSpaceSquareFeet"]) - 300.0) < 0.001

    # also verify room entry exists
    assert len(employee["Rooms"]) == 1
    assert employee["Rooms"][0]["EmployeeShareSquareFeet"] == 300.0