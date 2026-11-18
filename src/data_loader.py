"""
data_loader.py - loads the expense CSV and cleans it.

Cleaning steps (each one is counted in the returned log):
  1. Check required columns exist
  2. Convert date and amount to proper types
  3. Remove rows with bad dates, bad amounts or amounts <= 0
  4. Standardise category and payment method spelling
  5. Fill missing descriptions
  6. Remove exact duplicate rows
  7. Add helper columns (month, weekday, is_weekend)
"""
import pandas as pd

from src import config

REQUIRED_COLUMNS = {"date", "category", "amount", "payment_method", "description"}

_CATEGORY_LOOKUP = {c.lower(): c for c in config.CATEGORIES}
_CATEGORY_LOOKUP.update(config.CATEGORY_ALIASES)


def _clean_text(value):
    """Lower-case, trim and collapse repeated spaces."""
    return " ".join(str(value).lower().split())


def normalise_category(value):
    """Map any spelling of a category to a standard name (unknown -> Other)."""
    return _CATEGORY_LOOKUP.get(_clean_text(value), "Other")


def normalise_payment(value):
    """Map any spelling of a payment method to a standard name."""
    if pd.isna(value):
        return "Unknown"
    return config.PAYMENT_ALIASES.get(_clean_text(value), str(value).strip().title())


def clean_expenses(raw):
    """Clean a raw expenses DataFrame. Returns (clean_df, log_dict)."""
    df = raw.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    log = {"rows_loaded": len(df)}

    # Step 2-3: types + remove invalid rows
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    invalid = df["date"].isna() | df["amount"].isna() | (df["amount"] <= 0)
    log["invalid_rows_removed"] = int(invalid.sum())
    df = df[~invalid].copy()

    # Step 4: standardise text columns
    before = df["category"].astype(str).copy()
    df["category"] = df["category"].map(normalise_category)
    log["category_values_fixed"] = int((before != df["category"]).sum())
    df["payment_method"] = df["payment_method"].map(normalise_payment)

    # Step 5: missing descriptions
    log["missing_descriptions_filled"] = int(df["description"].isna().sum())
    df["description"] = df["description"].fillna("No description").astype(str).str.strip()

    # Step 6: duplicates (checked AFTER standardising so messy copies match too)
    size = len(df)
    df = df.drop_duplicates(
        subset=["date", "category", "amount", "payment_method", "description"])
    log["duplicates_removed"] = size - len(df)

    # Step 7: helper columns used by the analysis
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.dayofweek >= 5

    df = df.sort_values("date").reset_index(drop=True)
    log["rows_after_cleaning"] = len(df)
    return df, log


def load_expenses(csv_path=None):
    """Read the CSV file and return (clean_df, log)."""
    csv_path = csv_path or config.DEFAULT_CSV
    raw = pd.read_csv(csv_path)
    return clean_expenses(raw)
