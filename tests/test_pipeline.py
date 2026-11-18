"""Basic tests. Run with:  python -m pytest"""
import pandas as pd

from src import analysis, data_generator, data_loader


def make_clean_df():
    raw = data_generator.add_dirty_rows(data_generator.generate_expenses())
    return data_loader.clean_expenses(raw)


def test_cleaning_removes_bad_rows_and_duplicates():
    df, log = make_clean_df()
    assert log["invalid_rows_removed"] == 3      # 'abc', bad date, negative amount
    assert log["duplicates_removed"] == 3        # 3 copied rows
    assert df["amount"].gt(0).all()
    assert df["date"].notna().all()


def test_categories_are_standardised():
    df, _ = make_clean_df()
    allowed = set(data_loader.config.CATEGORIES)
    assert set(df["category"]).issubset(allowed)
    assert "GROCERIES" not in set(df["category"])


def test_normalise_helpers():
    assert data_loader.normalise_category("  food & dining ") == "Food & Dining"
    assert data_loader.normalise_category("travel") == "Transport"
    assert data_loader.normalise_category("???") == "Other"
    assert data_loader.normalise_payment("gpay") == "UPI"


def test_category_totals_add_up_to_total_spending():
    df, _ = make_clean_df()
    cats = analysis.category_summary(df)
    assert abs(cats["total"].sum() - df["amount"].sum()) < 0.5
    assert abs(cats["share_pct"].sum() - 100) < 0.5


def test_partial_month_is_detected():
    df, _ = make_clean_df()
    monthly = analysis.monthly_summary(df)
    assert monthly.iloc[-1]["is_partial"]        # data stops on 15 November
    assert not monthly.iloc[0]["is_partial"]


def test_daily_spending_has_one_row_per_day():
    df, _ = make_clean_df()
    daily = analysis.daily_spending(df)
    assert len(daily) == (df["date"].max() - df["date"].min()).days + 1


def test_missing_column_raises_clear_error():
    bad = pd.DataFrame({"date": ["2026-01-01"], "amount": [10]})
    try:
        data_loader.clean_expenses(bad)
        assert False, "should have raised ValueError"
    except ValueError as err:
        assert "missing required columns" in str(err)
