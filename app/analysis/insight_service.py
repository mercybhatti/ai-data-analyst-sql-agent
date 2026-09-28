from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY
from app.analysis.result_analyzer import format_analysis_for_llm


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
You are a professional data analyst.

Your job is to explain SQL query results in simple,
accurate business language.

Rules:

1. Base your explanation only on the provided query result
   and analysis.
2. Do not invent facts or numbers.
2.5. When reporting numeric values, copy the exact value from the
     query result. Never truncate, round, abbreviate, or partially
     reproduce a numeric value unless the user explicitly asks for
     rounding.
3. Directly answer the user's question.
4. Mention important patterns or notable values when relevant.
5. Keep the response concise and professional.
6. Do not mention internal implementation details.
7. Do not generate SQL.
8. Do not use Markdown tables.
9. If the result is empty, clearly state that no matching data
   was found.
"""


# ============================================================
# INSIGHT GENERATION
# ============================================================

def generate_insight(
    user_question: str,
    dataframe,
) -> str:
    """
    Generate a natural-language business insight from
    a SQL result DataFrame.
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

    analysis = format_analysis_for_llm(
        dataframe
    )

    result_preview = dataframe.head(20).to_string(
        index=False
    )

    prompt = f"""
User question:

{question}

Query result:

{result_preview}

Data analysis:

{analysis}

Explain the result and directly answer the user's question.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=300,
        ),
        )

    except Exception:

        try:
            response = client.models.generate_content(
                model=FALLBACK_MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    max_output_tokens=300,
            ),
            )

        except Exception as exc:
            raise RuntimeError(
                f"Gemini insight generation failed: {exc}"
            ) from exc

    insight = response.text.strip()

    if not insight:
        raise RuntimeError(
            "Gemini returned an empty insight."
        )

    return insight


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    import pandas as pd

    test_data = pd.DataFrame(
        {
            "state": [
                "Georgia",
                "Virginia",
                "South Dakota",
                "Florida",
                "Illinois",
            ],
            "customer_count": [
                18,
                15,
                15,
                15,
                14,
            ],
        }
    )

    question = "Which state has the most customers?"

    print("User question:")
    print(question)

    print()
    print("Generating AI insight...")
    print("=" * 60)

    insight = generate_insight(
        user_question=question,
        dataframe=test_data,
    )

    print()
    print("AI Insight:")
    print(insight)