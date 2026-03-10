import pytest


class FakeCursor:
    def __init__(self, events):
        self.events = events
        self.last_query = ""
        self.result_one = None

    def execute(self, query, params=None):
        self.last_query = " ".join(query.split())
        if self.last_query.startswith("SELECT Quantity FROM RoomsAreEquippedWithEquipment"):
            self.result_one = {"Quantity": 2}
        else:
            self.result_one = None

        if self.last_query.startswith("UPDATE RoomsAreEquippedWithEquipment"):
            self.events.append("update")
        if self.last_query.startswith("INSERT INTO RoomsAreEquippedWithEquipment"):
            self.events.append("insert")
        if self.last_query.startswith("DELETE FROM RoomsAreEquippedWithEquipment"):
            self.events.append("delete")

    def fetchone(self):
        return self.result_one

    def fetchall(self):
        return []

    def close(self):
        pass


class FakeConn:
    def __init__(self, events):
        self.events = events
        self.committed = False
        self.rolled_back = False

    def cursor(self, dictionary=False):
        return FakeCursor(self.events)

    def commit(self):
        self.committed = True
        self.events.append("commit")

    def rollback(self):
        self.rolled_back = True
        self.events.append("rollback")


@pytest.fixture
def events():
    return []


@pytest.fixture
def fake_conn(events):
    return FakeConn(events)
