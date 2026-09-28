from sqlalchemy import inspect

from app.database.database import engine


# ============================================================
# TABLES THAT SHOULD NEVER BE EXPOSED TO THE LLM
# ============================================================

EXCLUDED_TABLES = {
    "users",
    "datasets",
}


# ============================================================
# DATABASE SCHEMA
# ============================================================

def get_database_schema() -> dict:
    """
    Return the database schema for user-queryable data tables.

    Internal application tables such as users and datasets
    are excluded from the LLM-facing schema.
    """

    inspector = inspect(engine)

    schema = {}

    for table_name in inspector.get_table_names():
        if table_name in EXCLUDED_TABLES:
            continue

        columns = inspector.get_columns(table_name)

        table_schema = {
            "table_name": table_name,
            "columns": [],
        }

        for column in columns:
            table_schema["columns"].append(
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": bool(column["nullable"]),
                }
            )

        schema[table_name] = table_schema

    return schema


# ============================================================
# LLM-FRIENDLY SCHEMA
# ============================================================

def format_schema_for_llm() -> str:
    
    """
    Convert the database schema into a compact text format
    suitable for an LLM prompt.
    """

    schema = get_database_schema()

    if not schema:
        return "No queryable database tables are available."

    lines = []

    for table_name, table_info in schema.items():
        lines.append(f"TABLE: {table_name}")

        for column in table_info["columns"]:
            nullable = "NULL" if column["nullable"] else "NOT NULL"

            lines.append(
                f"  - {column['name']} "
                f"({column['type']}, {nullable})"
            )

        lines.append("")

    return "\n".join(lines).strip()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("LLM-Queryable Database Schema")
    print("=" * 60)
    print(format_schema_for_llm())


# ============================================================
# SINGLE TABLE SCHEMA FOR LLM
# ============================================================

def format_table_schema_for_llm(
    table_name: str,
) -> str:
    """
    Return the schema for one specific queryable table.
    """

    schema = get_database_schema()

    if table_name not in schema:
        raise ValueError(
            f"Dataset table '{table_name}' was not found."
        )

    table_info = schema[table_name]

    lines = [
        f"TABLE: {table_name}"
    ]

    for column in table_info["columns"]:

        nullable = (
            "NULL"
            if column["nullable"]
            else "NOT NULL"
        )

        lines.append(
            f"  - {column['name']} "
            f"({column['type']}, {nullable})"
        )

    return "\n".join(lines)