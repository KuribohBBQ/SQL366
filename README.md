# CSC 366 Final Project Demo

repo link: https://github.com/KuribohBBQ/SQL366

## main files

- api code: `api/main.py`
- db connection helper: `api/database.py`
- instructor demo script: `professor_demo_script.py`
- client demo script: `final_demo_script.py`
- quick single-call harness: `demo_harness.py`
- old lab harness (still usable): `lab4_harness.py`

## db config

this project reads db values from `api/.env`.

example:

```env
DB_HOST=mysql.labthreesixfive.com
DB_PORT=3306
DB_USER=yottabank
DB_PASSWORD=your_password_here
DB_NAME=yottabank
```

`lab4_harness.py` uses `settings.config` instead.

## install

```bash
python -m pip install fastapi mysql-connector-python python-dotenv pytest httpx
```

## run demo scripts

instructor demo:

```bash
python professor_demo_script.py > instructor_demo_output.txt
```

client demo:

```bash
python final_demo_script.py > client_demo_output.txt
```

quick speaking/checklist doc:

- `DEMO_CHECKLIST.md`

quick harness (for ad-hoc checks during demo):

```bash
python demo_harness.py
```

## run tests

```bash
python -m pytest -q tests
```

## final demo notes

- keep two scripts to avoid update conflicts during parallel demos.
- after API calls that create logs, call `/getLatestLog` (this is our implementation of the spec's "getLastLogRecord").
- make sure output files clearly show action text + returned data/error.

## quick pre-demo checklist

- DB has floorplans/buildings/rooms/departments/employees/equipment loaded.
- DB has room assignments (room->dept, employee->room, equipment->room).
- DB has all 5 roles: Administrator, College Update, Department Update, College View, Department View.
- DB has required demo users across those roles and colleges/departments.
- run instructor + client scripts separately and save outputs for review.

## quick db review commands (for instructor prompts)

```sql
SHOW TABLES;
SHOW CREATE TABLE Rooms;
SHOW CREATE TABLE Users;
SELECT * FROM Roles;
SELECT COUNT(*) FROM Logs;
```
