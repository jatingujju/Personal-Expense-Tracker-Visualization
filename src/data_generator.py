"""
data_generator.py - creates SYNTHETIC (fake but realistic) expense data.

Why? You do not have access to real bank data, so we simulate six months of
spending. A few "dirty" rows (messy spelling, duplicates, bad values) are
added ON PURPOSE so the cleaning step has something real to fix.
"""
import numpy as np
import pandas as pd

from src import config

# (category, low, high, notes) - typical amount range and sample descriptions
SPENDING_PROFILE = {
    "Groceries": (100, 900, ["Vegetables", "Supermarket", "Milk and bread", "Monthly staples"]),
    "Food & Dining": (60, 450, ["Lunch", "Dinner out", "Coffee", "Zomato order", "Swiggy order"]),
    "Transport": (20, 300, ["Auto ride", "Metro card", "Petrol", "Cab ride", "Bus pass"]),
    "Shopping": (300, 2500, ["Clothes", "Online order", "Shoes", "Gadget accessory"]),
    "Entertainment": (80, 700, ["Movie ticket", "OTT subscription", "Gaming", "Concert"]),
    "Health": (100, 1200, ["Pharmacy", "Doctor visit", "Gym fee", "Lab test"]),
    "Education": (100, 1500, ["Online course", "Books", "Exam fee", "Stationery"]),
    "Bills & Utilities": (150, 700, ["Mobile recharge", "Water bill", "Gas cylinder"]),
}

# How likely each category is for a random daily purchase (sums to 1)
CATEGORY_WEIGHTS = {
    "Groceries": 0.22,
    "Food & Dining": 0.30,
    "Transport": 0.20,
    "Shopping": 0.08,
    "Entertainment": 0.07,
    "Health": 0.04,
    "Education": 0.04,
    "Bills & Utilities": 0.05,
}

# Which payment method is most common (sums to 1)
PAYMENT_WEIGHTS = {"UPI": 0.50, "Cash": 0.15, "Credit Card": 0.15,
                   "Debit Card": 0.12, "Net Banking": 0.08}


def generate_expenses(start="2026-06-01", end="2026-11-15", seed=42):
    """Return a DataFrame of simulated daily expenses."""
    rng = np.random.default_rng(seed)  # fixed seed = same data every run
    rows = []

    cats = list(CATEGORY_WEIGHTS.keys())
    cat_p = list(CATEGORY_WEIGHTS.values())
    pays = list(PAYMENT_WEIGHTS.keys())
    pay_p = list(PAYMENT_WEIGHTS.values())

    for day in pd.date_range(start, end):
        # --- Fixed monthly items ---
        if day.day == 1:
            rows.append((day, "Rent", 12000.00, "Net Banking", "Monthly rent"))
        if day.day == 5:
            rows.append((day, "Bills & Utilities", round(rng.uniform(800, 1800), 2),
                         "UPI", "Electricity bill"))
        if day.day == 10:
            rows.append((day, "Bills & Utilities", 699.00, "Debit Card", "Broadband bill"))

        # --- Random everyday purchases (more on weekends) ---
        average_purchases = 1.6 if day.dayofweek >= 5 else 1.0
        for _ in range(rng.poisson(average_purchases)):
            category = rng.choice(cats, p=cat_p)
            low, high, notes = SPENDING_PROFILE[category]
            amount = round(float(rng.uniform(low, high)), 2)
            payment = rng.choice(pays, p=pay_p)
            rows.append((day, category, amount, payment, rng.choice(notes)))

    df = pd.DataFrame(rows, columns=["date", "category", "amount",
                                     "payment_method", "description"])
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df


def add_dirty_rows(df):
    """Append a few messy rows to demonstrate data cleaning."""
    dirty = pd.DataFrame([
        # inconsistent spelling / spacing / capital letters
        ("2026-07-14", "  food & dining ", 240.00, "upi", "Lunch with friends"),
        ("2026-08-03", "GROCERIES", 612.50, "CASH", "Supermarket"),
        ("2026-09-09", "travel", 180.00, "gpay", "Auto ride"),
        # missing description
        ("2026-10-02", "Shopping", 999.00, "Credit Card", None),
        # invalid values the cleaner must remove
        ("2026-10-11", "Food & Dining", "abc", "UPI", "Typing mistake"),
        ("not a date", "Transport", 120.00, "Cash", "Broken date"),
        ("2026-10-20", "Entertainment", -500.00, "UPI", "Negative amount"),
    ], columns=df.columns)

    # exact duplicate rows (e.g. a bank statement exported twice)
    duplicates = df.sample(3, random_state=1)
    return pd.concat([df, dirty, duplicates], ignore_index=True)


def create_sample_csv(path=None, **kwargs):
    """Generate data, add messy rows and save to CSV. Returns the path."""
    path = path or config.DEFAULT_CSV
    path.parent.mkdir(parents=True, exist_ok=True)
    df = add_dirty_rows(generate_expenses(**kwargs))
    df.to_csv(path, index=False)
    return path
