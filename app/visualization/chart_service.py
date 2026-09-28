import pandas as pd
import plotly.express as px
import json


# ============================================================
# CHART TYPE DETECTION
# ============================================================

def detect_chart_type(
    dataframe: pd.DataFrame,
) -> str | None:
    """
    Detect a suitable chart type based on the structure
    of the SQL result DataFrame.

    Returns:
        "bar", "line", "pie", "scatter", or None
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError(
            "Input must be a Pandas DataFrame."
        )

    if dataframe.empty:
        return None

    if len(dataframe.columns) < 2:
        return None

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    categorical_columns = dataframe.select_dtypes(
        include=["str", "object", "category"]
    ).columns

    # --------------------------------------------------------
    # One categorical + one numeric column
    # --------------------------------------------------------

    if (
        len(categorical_columns) >= 1
        and len(numeric_columns) >= 1
    ):
        return "bar"

    # --------------------------------------------------------
    # Two numeric columns
    # --------------------------------------------------------

    if len(numeric_columns) >= 2:
        return "scatter"

    return None


# ============================================================
# BAR CHART
# ============================================================

def create_bar_chart(
    dataframe: pd.DataFrame,
):
    """
    Create a Plotly bar chart for one categorical
    and one numeric column.
    """

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    categorical_columns = dataframe.select_dtypes(
        include=["str", "object", "category"]
    ).columns

    if (
        len(categorical_columns) == 0
        or len(numeric_columns) == 0
    ):
        return None

    x_column = categorical_columns[0]
    y_column = numeric_columns[0]

    return px.bar(
        dataframe,
        x=x_column,
        y=y_column,
        title=f"{y_column} by {x_column}",
    )


# ============================================================
# SCATTER CHART
# ============================================================

def create_scatter_chart(
    dataframe: pd.DataFrame,
):
    """
    Create a Plotly scatter chart for two numeric columns.
    """

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) < 2:
        return None

    x_column = numeric_columns[0]
    y_column = numeric_columns[1]

    return px.scatter(
        dataframe,
        x=x_column,
        y=y_column,
        title=f"{y_column} vs {x_column}",
    )


# ============================================================
# AUTOMATIC CHART GENERATION
# ============================================================

def create_chart(
    dataframe: pd.DataFrame,
):
    """
    Automatically select and create an appropriate
    Plotly chart.
    """

    chart_type = detect_chart_type(
        dataframe
    )

    if chart_type == "bar":
        return create_bar_chart(
            dataframe
        )

    if chart_type == "scatter":
        return create_scatter_chart(
            dataframe
        )

    return None


# ============================================================
# CHART → JSON
# ============================================================

def chart_to_json(chart) -> dict | None:
    """
    Convert a Plotly Figure into a JSON-serializable
    dictionary that can be returned by the API.
    """

    if chart is None:
        return None

    return json.loads(
        chart.to_json()
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    test_data = pd.DataFrame(
        {
            "state": [
                "Georgia",
                "Virginia",
                "Florida",
                "Illinois",
                "Alabama",
            ],
            "customer_count": [
                18,
                15,
                15,
                14,
                13,
            ],
        }
    )

    chart_type = detect_chart_type(
        test_data
    )

    print("Detected chart type:")
    print(chart_type)

    chart = create_chart(
        test_data
    )

    if chart is not None:
        chart.write_html(
            "chart_test.html"
        )

        chart_json = chart_to_json(
            chart
        )

        print()
        print(
            "Chart created successfully!"
        )

        print(
            "Chart JSON conversion successful:"
        )

        print(
            isinstance(chart_json, dict)
        )

        print(
            "Saved as: chart_test.html"
        )
    else:
        print(
            "No suitable chart could be generated."
        )