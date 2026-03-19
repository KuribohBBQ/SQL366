# CSC 366 Lab 4

## where stuff is

- api code: `api/main.py`
- db helper: `api/database.py`
- test/demo harness: `lab4_harness.py`
- tests: `tests/`

## github

https://github.com/KuribohBBQ/SQL366

## make settings.config

use this format:

```ini
[mysql]
host=mysql.labthreesixfive.com
port=3306
user=yottabank
password=...
database=yottabank
```

## run

install packages:

```bash
python -m pip install fastapi mysql-connector-python python-dotenv pytest httpx
```

run tests:

```bash
python -m pytest -q tests
```

run harness:

```bash
python lab4_harness.py
```

save harness output to file:

```bash
python lab4_harness.py > demo_output.txt
```

## what harness does

- calls permission checks
- calls read endpoints
- calls update endpoint
- shows one permission fail case
- calls log endpoints
