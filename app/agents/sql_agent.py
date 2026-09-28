import time

from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY
from app.services.schema_service import format_table_schema_for_llm


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY,
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-3.8-flash"
FALLBACK_MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are an expert SQL analyst for an AI data analysis application.

Your job is to convert a user's natural-language data question
into ONE valid SQLite SQL query.

Rules:

1. Generate ONLY SQL.
2. Do not use Markdown.
3. Do not wrap SQL in code fences.
4. Only generate read-only queries.
5. Use SELECT statements or WITH ... SELECT statements.
6. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE,
   TRUNCATE, REPLACE, ATTACH, DETACH, VACUUM, PRAGMA, or other
   database-modifying operations.
7. Use only tables and columns present in the provided schema.
8. Do not query internal application tables.
9. Prefer clear column aliases for calculated values.
10. Use SQLite-compatible SQL syntax.
11. If aggregation is required, use appropriate GROUP BY clauses.
12. If multiple tables are needed, use appropriate JOIN conditions.
13. Do not invent tables or columns.
14. Return exactly one SQL query and nothing else.
"""


# ============================================================
# SQL GENERATION
# ============================================================

def generate_sql(
    user_question: str,
    table_name: str,
) -> str:
    """
    Generate a read-only SQLite SQL query from a natural-language
    user question using Gemini.
    """

    if not isinstance(user_question, str):
        raise ValueError(
            "User question must be a string."
        )

    question = user_question.strip()

    if not question:
        raise ValueError(
            "User question cannot be empty."
        )

    schema = format_table_schema_for_llm(
        table_name
    )

    prompt = f"""
Database schema:

{schema}

The query must use ONLY the table and columns provided above.

User question:

{question}

Generate the SQLite SQL query that answers the user's question.
Return only the SQL query.
"""

    models_to_try = [
        MODEL_NAME,
        FALLBACK_MODEL_NAME,
    ]

    last_error = None

    for model_name in models_to_try:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.1,
                        max_output_tokens=500,
                    ),
                )

                break

            except Exception as exc:

                last_error = exc

                if attempt < 2:
                    time.sleep(
                        2 ** attempt
                    )

        else:
            continue

        break

    else:

        raise RuntimeError(
            f"Gemini SQL generation failed: {last_error}"
        ) from last_error

    generated_sql = response.text.strip()

    if not generated_sql:
        raise RuntimeError(
            "Gemini returned an empty SQL response."
        )

    # Remove accidental Markdown code fences if the model
    # returns them despite the instruction.
    if generated_sql.startswith("```"):

        generated_sql = generated_sql.replace(
            "```sql",
            "",
            1,
        ).replace(
            "```",
            "",
        ).strip()

    return generated_sql


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    question = "Which state has the most customers?"

    print("User question:")
    print(question)

    print()
    print("Generated SQL:")
    print("=" * 60)

    sql = generate_sql(
        question,
        "customers",
    )

    print(sql)