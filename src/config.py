"""
config.py - central settings for the Personal Expense Tracker.

Everything you might want to tweak (paths, categories, budgets, income)
lives here, so the other files stay clean.
"""
from pathlib import Path

# ---------- Folder paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
IMAGE_DIR = BASE_DIR / "images"
REPORT_DIR = BASE_DIR / "reports"
DEFAULT_CSV = DATA_DIR / "expenses.csv"

# ---------- Money settings ----------
# "Rs." is used instead of the rupee symbol so output also prints
# correctly in older Windows terminals.
CURRENCY = "Rs."
# Assumed monthly income/allowance. Change it to your own number.
MONTHLY_INCOME = 35000

# ---------- Categories and payment methods ----------
CATEGORIES = [
    "Rent",
    "Groceries",
    "Food & Dining",
    "Transport",
    "Bills & Utilities",
    "Shopping",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]

PAYMENT_METHODS = ["UPI", "Cash", "Credit Card", "Debit Card", "Net Banking"]

# Monthly budget limit per category (used for overspending alerts)
MONTHLY_BUDGETS = {
    "Rent": 12000,
    "Groceries": 5000,
    "Food & Dining": 3500,
    "Transport": 2000,
    "Bills & Utilities": 3000,
    "Shopping": 3000,
    "Entertainment": 1500,
    "Health": 1500,
    "Education": 1500,
}

# Alternative spellings that the cleaner should map to a standard category
CATEGORY_ALIASES = {
    "food": "Food & Dining",
    "food and dining": "Food & Dining",
    "dining": "Food & Dining",
    "eating out": "Food & Dining",
    "grocery": "Groceries",
    "bills": "Bills & Utilities",
    "utilities": "Bills & Utilities",
    "bills and utilities": "Bills & Utilities",
    "travel": "Transport",
    "transportation": "Transport",
    "fun": "Entertainment",
    "medical": "Health",
    "healthcare": "Health",
    "study": "Education",
}

# Alternative spellings for payment methods
PAYMENT_ALIASES = {
    "upi": "UPI",
    "gpay": "UPI",
    "phonepe": "UPI",
    "cash": "Cash",
    "credit card": "Credit Card",
    "credit": "Credit Card",
    "debit card": "Debit Card",
    "debit": "Debit Card",
    "net banking": "Net Banking",
    "netbanking": "Net Banking",
}
