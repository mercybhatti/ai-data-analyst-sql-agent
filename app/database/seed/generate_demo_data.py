from pathlib import Path
from random import choice, randint, uniform
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


# ============================================================
# CONFIGURATION
# ============================================================

fake = Faker()

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "demo"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

CUSTOMER_COUNT = 500
PRODUCT_COUNT = 100
ORDER_COUNT = 2000


# ============================================================
# CONSTANTS
# ============================================================

CATEGORIES = [
    "Electronics",
    "Home & Kitchen",
    "Clothing",
    "Books",
    "Sports",
    "Beauty",
]

PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Cash on Delivery",
]

ORDER_STATUSES = [
    "Completed",
    "Completed",
    "Completed",
    "Shipped",
    "Processing",
    "Cancelled",
]


# ============================================================
# CUSTOMER DATA
# ============================================================

def generate_customers():
    """Generate synthetic customer records."""

    customers = []

    for customer_id in range(1, CUSTOMER_COUNT + 1):

        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": fake.name(),
                "email": fake.unique.email(),
                "city": fake.city(),
                "state": fake.state(),
                "country": "India",
                "signup_date": fake.date_between(
                    start_date="-3y",
                    end_date="today",
                ),
            }
        )

    return pd.DataFrame(customers)


# ============================================================
# PRODUCT DATA
# ============================================================

def generate_products():
    """Generate synthetic product records."""

    products = []

    for product_id in range(1, PRODUCT_COUNT + 1):

        category = choice(CATEGORIES)

        products.append(
            {
                "product_id": product_id,
                "product_name": fake.catch_phrase(),
                "category": category,
                "price": round(
                    uniform(300, 100000),
                    2,
                ),
                "stock_quantity": randint(
                    10,
                    500,
                ),
            }
        )

    return pd.DataFrame(products)


# ============================================================
# ORDER DATA
# ============================================================

def generate_orders(customers, products):
    """Generate synthetic order records."""

    orders = []

    start_date = datetime.now() - timedelta(
        days=730
    )

    for order_id in range(1, ORDER_COUNT + 1):

        customer = customers.sample(
            n=1
        ).iloc[0]

        product = products.sample(
            n=1
        ).iloc[0]

        quantity = randint(
            1,
            5,
        )

        unit_price = float(
            product["price"]
        )

        discount_percent = round(
            uniform(0, 25),
            2,
        )

        subtotal = quantity * unit_price

        discount_amount = (
            subtotal * discount_percent / 100
        )

        total_amount = (
            subtotal - discount_amount
        )

        order_date = (
            start_date
            + timedelta(
                days=randint(
                    0,
                    730,
                ),
                hours=randint(
                    0,
                    23,
                ),
                minutes=randint(
                    0,
                    59,
                ),
            )
        )

        orders.append(
            {
                "order_id": order_id,
                "customer_id": int(
                    customer["customer_id"]
                ),
                "product_id": int(
                    product["product_id"]
                ),
                "order_date": order_date,
                "quantity": quantity,
                "unit_price": round(
                    unit_price,
                    2,
                ),
                "discount_percent": discount_percent,
                "total_amount": round(
                    total_amount,
                    2,
                ),
                "payment_method": choice(
                    PAYMENT_METHODS
                ),
                "order_status": choice(
                    ORDER_STATUSES
                ),
            }
        )

    return pd.DataFrame(orders)


# ============================================================
# SAVE DATASETS
# ============================================================

def save_datasets():
    """Generate and save all demo datasets as CSV files."""

    print("Generating demo datasets...")

    customers = generate_customers()

    products = generate_products()

    orders = generate_orders(
        customers,
        products,
    )

    customers_path = (
        DATA_DIR / "customers.csv"
    )

    products_path = (
        DATA_DIR / "products.csv"
    )

    orders_path = (
        DATA_DIR / "orders.csv"
    )

    customers.to_csv(
        customers_path,
        index=False,
    )

    products.to_csv(
        products_path,
        index=False,
    )

    orders.to_csv(
        orders_path,
        index=False,
    )

    print()
    print("Demo datasets generated successfully!")
    print()
    print(
        f"Customers : {len(customers)} rows"
    )
    print(
        f"Products  : {len(products)} rows"
    )
    print(
        f"Orders    : {len(orders)} rows"
    )
    print()
    print(
        f"Saved to: {DATA_DIR}"
    )


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    save_datasets()