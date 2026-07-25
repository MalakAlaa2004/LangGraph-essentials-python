import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not set in .env")
    sys.exit(1)


def test_connection():
    print(f"Connecting to database: {DATABASE_URL.split('@')[-1]}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            row = result.fetchone()
            print(" Database Connection Successful!")
            print(f"PostgreSQL Version: {row[0]}")

            # Check user role
            user_res = connection.execute(text("SELECT current_user;"))
            user_row = user_res.fetchone()
            print(f"Connected as User: {user_row[0]}")
            return True
    except Exception as e:
        print(f" Database Connection Failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    if not success:
        sys.exit(1)
