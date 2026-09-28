import pandas as pd
from app.services.sql_service import run_sql_query

# ============================================================
# BASIC RESULT ANALYSIS
# ============================================================

def analyze_dataframe(dataframe: pd.DataFrame) -> dict:
    """
    Analyze a SQL result DataFrame and return useful
    statistical and structural information.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError(
            "Input must be a Pandas DataFrame."
        )

    if dataframe.empty:
        return {
            "row_count": 0,
            "column_count": int(len(dataframe.columns)),
            "columns": [],
            "numeric_summary": {},
            "categorical_summary": {},
            "null_summary": {},
        }

    analysis = {
        "row_count": int(dataframe.shape[0]),
        "column_count": int(dataframe.shape[1]),
        "columns": [
            str(column)
            for column in dataframe.columns
        ],
        "numeric_summary": {},
        "categorical_summary": {},
        "null_summary": {},
    }

    # --------------------------------------------------------
    # NULL SUMMARY
    # --------------------------------------------------------

    for column in dataframe.columns:
        null_count = int(
            dataframe[column].isna().sum()
        )

        analysis["null_summary"][str(column)] = {
            "null_count": null_count,
            "null_percentage": round(
                (null_count / len(dataframe)) * 100,
                2,
            ),
        }

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:
        series = dataframe[column].dropna()

        if series.empty:
            continue

        analysis["numeric_summary"][str(column)] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "sum": round(float(series.sum()), 2),
        }

    # --------------------------------------------------------
    # CATEGORICAL / TEXT COLUMNS
    # --------------------------------------------------------

    categorical_columns = dataframe.select_dtypes(
        include=["object", "category", "bool"]
    ).columns

    for column in categorical_columns:
        value_counts = (
            dataframe[column]
            .dropna()
            .value_counts()
            .head(10)
        )

        analysis["categorical_summary"][str(column)] = {
            str(value): int(count)
            for value, count in value_counts.items()
        }

    return analysis


# ============================================================
# LLM-FRIENDLY RESULT SUMMARY
# ============================================================

def format_analysis_for_llm(
    dataframe: pd.DataFrame,
) -> str:
    """
    Convert DataFrame analysis into compact text
    that can later be passed to Gemini.
    """

    analysis = analyze_dataframe(dataframe)

    lines = [
        f"Rows: {analysis['row_count']}",
        f"Columns: {analysis['column_count']}",
    ]

    if analysis["numeric_summary"]:
        lines.append("")
        lines.append("NUMERIC COLUMNS:")

        for column, values in analysis[
            "numeric_summary"
        ].items():
            lines.append(
                f"- {column}: "
                f"min={values['min']}, "
                f"max={values['max']}, "
                f"mean={values['mean']}, "
                f"median={values['median']}, "
                f"sum={values['sum']}"
            )

    if analysis["categorical_summary"]:
        lines.append("")
        lines.append("CATEGORICAL COLUMNS:")

        for column, values in analysis[
            "categorical_summary"
        ].items():
            formatted_values = ", ".join(
                f"{key}={value}"
                for key, value in values.items()
            )

            lines.append(
                f"- {column}: {formatted_values}"
            )

    if analysis["null_summary"]:
        lines.append("")
        lines.append("NULL VALUES:")

        for column, values in analysis[
            "null_summary"
        ].items():
            if values["null_count"] > 0:
                lines.append(
                    f"- {column}: "
                    f"{values['null_count']} nulls "
                    f"({values['null_percentage']}%)"
                )

    return "\n".join(lines)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    from app.services.sql_service import run_sql_query

    result = run_sql_query(
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

    dataframe = result["data"]

    print("SQL Result:")
    print(dataframe)

    print()
    print("Analysis:")
    print("=" * 60)
    print(format_analysis_for_llm(dataframe))