from pathlib import Path

import pandas as pd

from app.database.database import engine


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = (
    BASE_DIR
    / "data"
    / "demo"
)


# ============================================================
# DATASET CONFIGURATION
# ============================================================

DATASETS = {
    "customers": DATA_DIR / "customers.csv",
    "products": DATA_DIR / "products.csv",
    "orders": DATA_DIR / "orders.csv",
}


# ============================================================
# LOAD DATA INTO DATABASE
# ============================================================

def load_demo_data():
    """
    Load generated CSV datasets into SQLite tables.
    """

    print("Loading demo datasets into SQLite...")

    for table_name, file_path in DATASETS.items():

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {file_path}"
            )

        dataframe = pd.read_csv(file_path)

        dataframe.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
        )

        print(
            f"✓ {table_name}: "
            f"{len(dataframe)} rows loaded"
        )

    print()
    print(
        "All demo datasets loaded successfully!"
    )


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    load_demo_data()