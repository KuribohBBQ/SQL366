# CSC 366 Lab 4

## Where the Lab 4 package is
- Package API implementation: `api/lab4_api.py`
- Shared error codes: `api/errors.py`
- Thin FastAPI wrappers: `api/main.py`

## Where the test/demo harness is
- Grader/demo harness: `lab4_harness.py`

## Create settings.config
Create a file named `settings.config` in the repo root with either format below.


## Run harness on unix1
From repo root:

```bash
python3 -m pip install -r requirements.txt 2>/dev/null || true
python3 -m pip install mysql-connector-python fastapi pydantic python-dotenv pytest
python3 lab4_harness.py
```

Redirect to file:

```bash
python3 lab4_harness.py > demo_output.txt
```

The harness prints the exact function name, input args, and returned result/error for each call and continues even if one call fails.

## Run tests
```bash
pytest -q
```
