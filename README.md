# CSC 366 Lab 4 (SQL366)

## Where the Lab 4 package is
- Package API implementation: `api/lab4_api.py`
- Shared error codes: `api/errors.py`
- Thin FastAPI wrappers (optional): `api/main.py`

## Where the test/demo harness is
- Grader/demo harness: `lab4_harness.py`

## Create `settings.config` (do not commit)
Create a file named `settings.config` in the repo root with either format below.

### INI format (recommended)
```ini
[mysql]
host=mysql.labthreesixfive.com
port=3306
user=yottabank
password=YOUR_PASSWORD
database=yottabank
```

### Flat key/value format
```text
host=mysql.labthreesixfive.com
port=3306
user=yottabank
password=YOUR_PASSWORD
database=yottabank
```

## Run harness on unix1
From repo root:

```bash
python3 -m pip install -r requirements.txt 2>/dev/null || true
python3 -m pip install mysql-connector-python fastapi pydantic python-dotenv pytest
python3 lab4_harness.py
```

Optional redirect to file:

```bash
python3 lab4_harness.py > demo_output.txt
```

The harness prints the exact function name, input args, and returned result/error for each call and continues even if one call fails.

## Run tests
```bash
pytest -q
```

## Notes for grading
- All DB-facing package functions accept a prepared `conn` object as first argument.
- Permission checks are performed at the start of each DB-facing function.
- Part 2 mutation functions perform write-ahead logging before mutation.
- `settings.config` is intentionally excluded from version control.
