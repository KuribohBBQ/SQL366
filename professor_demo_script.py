from dotenv import load_dotenv
import os
from fastapi.testclient import TestClient

load_dotenv()

from api import main as api_main
client = TestClient(api_main.app)

def main():
    # 1. List of Departments

    # 2. List of Floorplans

    # 3. List of Rooms

    # 4. Room Selection API

    # 5. List of Employees

    # 6. Employee Info

    # 7. Equipment Locations

    # 8. Enhanced Department List

    # 9. Addition of an Employee using all Roles

    # 10. Room Assignment to a person

    # 11. Department Room Assignment

    # 12. Add new equipment type / assign equipment to rooms

    # 13. Duplicate entries

    return


if __name__ == "__main__":
    main()

