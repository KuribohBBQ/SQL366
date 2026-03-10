import configparser
import os

try:
    import mysql.connector as mysql_connector
except ModuleNotFoundError:
    mysql_connector = None
from dotenv import load_dotenv

load_dotenv()


def load_settings(path: str = "settings.config") -> dict[str, str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing config file: {path}")

    parser = configparser.ConfigParser()
    with open(path, "r", encoding="utf-8") as handle:
        raw = handle.read().strip()

    if raw.startswith("["):
        parser.read_string(raw)
        section = "mysql" if parser.has_section("mysql") else parser.sections()[0]
        return {
            "host": parser.get(section, "host"),
            "port": parser.get(section, "port", fallback="3306"),
            "user": parser.get(section, "user"),
            "password": parser.get(section, "password"),
            "database": parser.get(section, "database"),
        }

    values: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip().lower()] = value.strip()

    return {
        "host": values["host"],
        "port": values.get("port", "3306"),
        "user": values["user"],
        "password": values["password"],
        "database": values.get("database") or values.get("db_name") or values["dbname"],
    }


def get_connection():
    if mysql_connector is None:
        raise ModuleNotFoundError("mysql-connector-python is required")
    return mysql_connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def get_connection_from_settings(path: str = "settings.config"):
    if mysql_connector is None:
        raise ModuleNotFoundError("mysql-connector-python is required")
    settings = load_settings(path)
    return mysql_connector.connect(
        host=settings["host"],
        port=int(settings["port"]),
        user=settings["user"],
        password=settings["password"],
        database=settings["database"],
    )


def test_connection():
    try:
        conn = get_connection()
        if conn.is_connected():
            conn.close()
            return True
    except Exception:
        return False
