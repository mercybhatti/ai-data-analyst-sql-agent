import re

import pandas as pd
from sqlalchemy import text

from app.database.database import engine


# ============================================================
# CONFIGURATION
# ============================================================

MAX_RESULT_ROWS = 1000


# ============================================================
# BLOCKED SQL OPERATIONS
# ============================================================

BLOCKED_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "ATTACH",
    "DETACH",
    "VACUUM",
    "PRAGMA",
    "REINDEX",
    "GRANT",
    "REVOKE",
    "MERGE",
    "CALL",
    "EXEC",
    "EXECUTE",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT",
    "RELEASE",
}


# ============================================================
# STRING LITERAL REMOVAL
# ============================================================

def remove_string_literals(sql: str) -> str:
    result = []
    index = 0

    while index < len(sql):
        character = sql[index]

        if character == "'":
            result.append(" ")
            index += 1

            while index < len(sql):
                if sql[index] == "'":
                    if (
                        index + 1 < len(sql)
                        and sql[index + 1] == "'"
                    ):
                        index += 2
                        continue

                    index += 1
                    break

                index += 1

            continue

        if character == '"':
            result.append(" ")
            index += 1

            while index < len(sql):
                if sql[index] == '"':
                    if (
                        index + 1 < len(sql)
                        and sql[index + 1] == '"'
                    ):
                        index += 2
                        continue

                    index += 1
                    break

                index += 1

            continue

        result.append(character)
        index += 1

    return "".join(result)


# ============================================================
# SQL VALIDATION
# ============================================================

def validate_sql(sql: str) -> str:
    if not isinstance(sql, str):
        raise ValueError(
            "SQL query must be a string."
        )

    query = sql.strip()

    if not query:
        raise ValueError(
            "SQL query cannot be empty."
        )

    # Allow one trailing semicolon.
    if query.endswith(";"):
        query = query[:-1].rstrip()

    # Block SQL comments.
    if "--" in query or "/*" in query or "*/" in query:
        raise ValueError(
            "SQL comments are not allowed."
        )

    # Block multiple SQL statements.
    if ";" in query:
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    inspection_query = remove_string_literals(
        query
    )

    normalized_query = re.sub(
        r"\s+",
        " ",
        inspection_query,
    ).strip()

    upper_query = normalized_query.upper()

    # Only SELECT / WITH queries are allowed.
    if not (
        upper_query.startswith("SELECT ")
        or upper_query == "SELECT"
        or upper_query.startswith("WITH ")
        or upper_query == "WITH"
    ):
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    # Block dangerous SQL operations.
    for keyword in BLOCKED_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            upper_query,
        ):
            raise ValueError(
                f"SQL operation '{keyword}' is not allowed."
            )

    # Validate WITH queries.
    if upper_query.startswith("WITH"):
        if not re.search(
            r"\bSELECT\b",
            upper_query,
        ):
            raise ValueError(
                "WITH queries must contain a SELECT statement."
            )

    return query


# ============================================================
# SQL EXECUTION
# ============================================================

def execute_sql(sql: str) -> pd.DataFrame:
    validated_sql = validate_sql(sql)

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(validated_sql)
            )

            rows = result.fetchmany(
                MAX_RESULT_ROWS
            )

            dataframe = pd.DataFrame(
                rows,
                columns=result.keys(),
            )

            return dataframe

    except Exception as exc:
        raise RuntimeError(
            f"SQL query execution failed: {exc}"
        ) from exc


# ============================================================
# RESULT SUMMARY
# ============================================================

def summarize_result(
    dataframe: pd.DataFrame,
) -> dict:
    return {
        "row_count": int(
            len(dataframe)
        ),
        "column_count": int(
            len(dataframe.columns)
        ),
        "columns": [
            str(column)
            for column in dataframe.columns
        ],
    }


# ============================================================
# COMPLETE SQL OPERATION
# ============================================================

def run_sql_query(sql: str) -> dict:
    dataframe = execute_sql(sql)

    summary = summarize_result(
        dataframe
    )

    return {
        "sql": sql,
        "data": dataframe,
        "summary": summary,
    }