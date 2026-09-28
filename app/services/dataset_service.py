from pathlib import Path
import re

import pandas as pd
from sqlalchemy import inspect

from app.database.database import engine


# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
}

MAX_FILE_SIZE_MB = 50


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_file(file_path: str | Path) -> Path:
    """
    Validate that the uploaded file exists,
    has a supported extension, and is within
    the allowed file size.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            "The provided path is not a file."
        )

    extension = path.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. "
            "Only CSV and XLSX files are allowed."
        )

    file_size_mb = (
        path.stat().st_size
        / (1024 * 1024)
    )

    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(
            f"File is too large. "
            f"Maximum allowed size is "
            f"{MAX_FILE_SIZE_MB} MB."
        )

    return path


# ============================================================
# DATASET READING
# ============================================================

def read_dataset(file_path: str | Path) -> pd.DataFrame:
    """
    Read a CSV or Excel dataset into a Pandas DataFrame.
    """

    path = validate_file(file_path)

    extension = path.suffix.lower()

    if extension == ".csv":
        dataframe = pd.read_csv(path)

    elif extension == ".xlsx":
        dataframe = pd.read_excel(path)

    else:
        raise ValueError(
            "Unsupported file type."
        )

    if dataframe.empty:
        raise ValueError(
            "The uploaded dataset is empty."
        )

    return dataframe


# ============================================================
# COLUMN NAME CLEANING
# ============================================================

def clean_column_names(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert column names into SQL-friendly names.
    """

    dataframe = dataframe.copy()

    cleaned_columns = []

    for column in dataframe.columns:

        name = str(column).strip().lower()

        name = re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            name,
        )

        name = re.sub(
            r"_+",
            "_",
            name,
        )

        name = name.strip("_")

        if not name:
            name = "column"

        if name[0].isdigit():
            name = f"column_{name}"

        cleaned_columns.append(name)

    # Make duplicate column names unique.
    seen = {}

    unique_columns = []

    for column in cleaned_columns:

        if column not in seen:
            seen[column] = 0
            unique_columns.append(column)

        else:
            seen[column] += 1

            unique_columns.append(
                f"{column}_{seen[column]}"
            )

    dataframe.columns = unique_columns

    return dataframe


# ============================================================
# TABLE NAME GENERATION
# ============================================================

def create_safe_table_name(
    dataset_name: str,
) -> str:
    """
    Convert a dataset name into a safe SQL table name.
    """

    table_name = dataset_name.strip().lower()

    table_name = re.sub(
        r"[^a-zA-Z0-9_]+",
        "_",
        table_name,
    )

    table_name = re.sub(
        r"_+",
        "_",
        table_name,
    )

    table_name = table_name.strip("_")

    if not table_name:
        table_name = "uploaded_dataset"

    if table_name[0].isdigit():
        table_name = f"dataset_{table_name}"

    return f"dataset_{table_name}"


# ============================================================
# SCHEMA PROFILING
# ============================================================

def profile_dataset(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Generate basic metadata about the dataset.
    """

    profile = {
        "row_count": int(
            dataframe.shape[0]
        ),
        "column_count": int(
            dataframe.shape[1]
        ),
        "columns": [],
    }

    for column in dataframe.columns:

        column_info = {
            "name": str(column),
            "dtype": str(
                dataframe[column].dtype
            ),
            "null_count": int(
                dataframe[column].isna().sum()
            ),
            "unique_count": int(
                dataframe[column].nunique(
                    dropna=True
                )
            ),
        }

        profile["columns"].append(
            column_info
        )

    return profile


# ============================================================
# DATABASE TABLE CREATION
# ============================================================

def save_dataset_to_database(
    dataframe: pd.DataFrame,
    table_name: str,
) -> dict:
    """
    Save a DataFrame as a SQL table.
    """

    inspector = inspect(engine)

    existing_tables = inspector.get_table_names()

    if table_name in existing_tables:
        raise ValueError(
            f"Table '{table_name}' already exists."
        )

    dataframe.to_sql(
        name=table_name,
        con=engine,
        if_exists="fail",
        index=False,
    )

    return {
        "table_name": table_name,
        "row_count": int(
            dataframe.shape[0]
        ),
        "column_count": int(
            dataframe.shape[1]
        ),
    }


# ============================================================
# COMPLETE DATASET PROCESSING PIPELINE
# ============================================================

def process_dataset(
    file_path: str | Path,
    dataset_name: str | None = None,
) -> dict:
    """
    Complete dataset ingestion pipeline.

    Steps:
    1. Validate file
    2. Read dataset
    3. Clean column names
    4. Profile schema
    5. Generate safe table name
    6. Save dataset to SQLite
    """

    path = validate_file(file_path)

    dataframe = read_dataset(path)

    dataframe = clean_column_names(
        dataframe
    )

    profile = profile_dataset(
        dataframe
    )

    if dataset_name is None:
        dataset_name = path.stem

    table_name = create_safe_table_name(
        dataset_name
    )

    database_info = save_dataset_to_database(
        dataframe=dataframe,
        table_name=table_name,
    )

    return {
        "dataset_name": dataset_name,
        "original_filename": path.name,
        "file_type": path.suffix.lower(),
        "table_name": database_info[
            "table_name"
        ],
        "row_count": database_info[
            "row_count"
        ],
        "column_count": database_info[
            "column_count"
        ],
        "profile": profile,
    }