
import sqlite3
from pathlib import Path

# The script is inside backend/, so its parent is the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "aidm.db"

print(f"Database path: {DATABASE_PATH}")

if not DATABASE_PATH.parent.exists():
    raise FileNotFoundError(
        f"Database directory not found: {DATABASE_PATH.parent}"
    )

connection = sqlite3.connect(DATABASE_PATH)

try:
    columns = [
        row[1]
        for row in connection.execute("PRAGMA table_info(users)")
    ]

    if not columns:
        raise RuntimeError(
            "No users table found. Check that this is the correct database."
        )

    if "location" not in columns:
        connection.execute(
            "ALTER TABLE users "
            "ADD COLUMN location VARCHAR NOT NULL DEFAULT 'Pune'"
        )
        connection.commit()
        print("Added location column successfully.")
    else:
        print("Location column already exists; no change needed.")

    updated_columns = [
        row[1]
        for row in connection.execute("PRAGMA table_info(users)")
    ]

    print("Users table columns:", updated_columns)

finally:
    connection.close()
