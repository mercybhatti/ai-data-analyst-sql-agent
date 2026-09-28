from sqlalchemy import inspect

from app.database.database import engine


# ============================================================
# DATABASE INSPECTION
# ============================================================

def check_database_tables():
    """
    Inspect the SQLite database and return
    the names of all existing tables.
    """

    inspector = inspect(engine)

    return inspector.get_table_names()


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    tables = check_database_tables()

    print("Database tables:")

    for table in tables:
        print(f"- {table}")