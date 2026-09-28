import pandas as pd

from app.analysis.insight_service import generate_insight
from app.analysis.result_analyzer import (
    analyze_dataframe,
    format_analysis_for_llm,
)
from app.visualization.chart_service import create_chart


def analyze_result(
    user_question: str,
    dataframe: pd.DataFrame,
) -> dict:
    """
    Run the complete analysis pipeline.

    Pipeline:
        SQL result
        -> DataFrame analysis
        -> AI insight
        -> automatic visualization
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

    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError(
            "Input result must be a Pandas DataFrame."
        )

    # --------------------------------------------------------
    # STEP 1: Analyze DataFrame
    # --------------------------------------------------------

    analysis = analyze_dataframe(
        dataframe
    )

    # --------------------------------------------------------
    # STEP 2: Format analysis for AI
    # --------------------------------------------------------

    formatted_analysis = format_analysis_for_llm(
        dataframe
    )

    # --------------------------------------------------------
    # STEP 3: Generate AI insight
    # --------------------------------------------------------

    insight = generate_insight(
        user_question=question,
        dataframe=dataframe,
    )

    # --------------------------------------------------------
    # STEP 4: Generate visualization
    # --------------------------------------------------------

    chart = create_chart(
        dataframe
    )

    # --------------------------------------------------------
    # STEP 5: Return complete result
    # --------------------------------------------------------

    return {
        "question": question,
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "data": dataframe,
        "analysis": analysis,
        "formatted_analysis": formatted_analysis,
        "insight": insight,
        "chart": chart,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    from app.services.sql_service import run_sql_query

    question = "Which state has the most customers?"

    print(
        "Running complete analysis pipeline..."
    )
    print("=" * 60)

    sql_result = run_sql_query(
        """
        SELECT
            state,
            COUNT(customer_id) AS customer_count
        FROM customers
        WHERE state IS NOT NULL
        GROUP BY state
        ORDER BY customer_count DESC
        LIMIT 10
        """
    )

    result = analyze_result(
        user_question=question,
        dataframe=sql_result["data"],
    )

    print()
    print("Question:")
    print(result["question"])

    print()
    print("SQL Result:")
    print(result["data"])

    print()
    print("AI Insight:")
    print(result["insight"])

    print()
    print("Chart:")
    if result["chart"] is not None:
        result["chart"].write_html(
            "analysis_chart_test.html"
        )
        print(
            "Chart created successfully!"
        )
        print(
            "Saved as: analysis_chart_test.html"
        )
    else:
        print(
            "No suitable chart generated."
        )