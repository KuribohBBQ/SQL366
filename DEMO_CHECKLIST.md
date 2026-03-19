# CSC 366 Final Demo Checklist

## 0) Before demo starts

- Confirm `api/.env` has working DB credentials.
- Confirm DB has required roles/users/assignments.
- Open two terminals:
  - Terminal A: instructor demo
  - Terminal B: client demo

## 1) Instructor demo run

```bash
python professor_demo_script.py > instructor_demo_output.txt
```

- Show script file quickly (`professor_demo_script.py`).
- Show output file (`instructor_demo_output.txt`).
- Point out: action text + returned results/errors are printed each step.

## 2) Client demo run

```bash
python final_demo_script.py > client_demo_output.txt
```

- Show script file quickly (`final_demo_script.py`).
- Show output file (`client_demo_output.txt`).
- Explain this script uses a separate update path to reduce conflicts.

## 3) for DB review

In MySQL:

```sql
SHOW TABLES;
SHOW CREATE TABLE Rooms;
SHOW CREATE TABLE Users;
SELECT * FROM Roles;
SELECT COUNT(*) FROM Logs;
```

## 4) for isolated API test

```bash
python demo_harness.py
```

- one-off checks
- For logging checks, call endpoint `/getLatestLog` after log-producing actions.

