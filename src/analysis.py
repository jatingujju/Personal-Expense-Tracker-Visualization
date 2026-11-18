"""
analysis.py - all the calculations. No plotting and no printing here:
each function takes the clean DataFrame and returns numbers or tables.
"""
import pandas as pd

from src import config


def overall_kpis(df):
    """Headline numbers for the whole period."""
    first, last = df["date"].min(), df["date"].max()
    n_days = (last - first).days + 1
    total = df["amount"].sum()

    by_cat = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    biggest = df.loc[df["amount"].idxmax()]
    by_day = df.groupby("date")["amount"].sum()

    return {
        "first_date": first,
        "last_date": last,
        "n_days": n_days,
        "total_spending": total,
        "n_transactions": len(df),
        "avg_transaction": df["amount"].mean(),
        "avg_daily_spending": total / n_days,
        "top_category": by_cat.index[0],
        "top_category_amount": by_cat.iloc[0],
        "biggest_expense_amount": biggest["amount"],
        "biggest_expense_desc": biggest["description"],
        "biggest_expense_date": biggest["date"],
        "busiest_day": by_day.idxmax(),
        "busiest_day_amount": by_day.max(),
    }


def category_summary(df):
    """Total, count, average and share (%) per category."""
    out = df.groupby("category")["amount"].agg(["sum", "count", "mean"])
    out.columns = ["total", "transactions", "average"]
    out["share_pct"] = out["total"] / out["total"].sum() * 100
    return out.sort_values("total", ascending=False).round(2).reset_index()


def payment_summary(df):
    """Total, count and share (%) per payment method."""
    out = df.groupby("payment_method")["amount"].agg(["sum", "count"])
    out.columns = ["total", "transactions"]
    out["share_pct"] = out["total"] / out["total"].sum() * 100
    return out.sort_values("total", ascending=False).round(2).reset_index()


def monthly_summary(df):
    """
    Monthly totals plus income/savings for COMPLETE months.
    A month is 'partial' when our data does not cover all of its days.
    """
    first, last = df["date"].min(), df["date"].max()
    rows = []
    for month, part in df.groupby("month"):
        period = pd.Period(month)
        start = max(first, period.start_time)
        end = min(last, period.end_time.normalize())
        covered = (end - start).days + 1
        partial = covered < period.days_in_month
        spent = part["amount"].sum()
        rows.append({
            "month": month,
            "total_spending": spent,
            "transactions": len(part),
            "days_covered": covered,
            "is_partial": partial,
            "avg_daily_spending": spent / covered,
            "income": float("nan") if partial else config.MONTHLY_INCOME,
            "savings": float("nan") if partial else config.MONTHLY_INCOME - spent,
        })
    out = pd.DataFrame(rows)
    out["savings_rate_pct"] = out["savings"] / out["income"] * 100
    return out.round(2)


def daily_spending(df, window=7):
    """Spending for every calendar day (0 on no-spend days) + moving average."""
    full_range = pd.date_range(df["date"].min(), df["date"].max())
    daily = df.groupby("date")["amount"].sum().reindex(full_range, fill_value=0)
    out = daily.rename("total").rename_axis("date").reset_index()
    out[f"moving_avg_{window}d"] = out["total"].rolling(window, min_periods=1).mean()
    # round only the number columns (rounding a date column triggers a warning)
    number_cols = ["total", f"moving_avg_{window}d"]
    out[number_cols] = out[number_cols].round(2)
    return out


def weekday_vs_weekend(df):
    """Average spending per day on weekdays versus weekends."""
    daily = daily_spending(df)
    daily["is_weekend"] = daily["date"].dt.dayofweek >= 5
    return daily.groupby("is_weekend")["total"].mean().round(2).rename(
        {False: "weekday", True: "weekend"})


def budget_check(df):
    """Compare each month's spending in each category with its budget."""
    spent = df.groupby(["month", "category"])["amount"].sum().reset_index()
    spent["budget"] = spent["category"].map(config.MONTHLY_BUDGETS)
    spent = spent.dropna(subset=["budget"]).copy()  # categories without a budget are skipped
    spent["over_by"] = (spent["amount"] - spent["budget"]).round(2)
    spent["status"] = spent["over_by"].apply(lambda x: "OVER BUDGET" if x > 0 else "ok")
    spent = spent.rename(columns={"amount": "spent"})
    return spent.sort_values(["month", "over_by"], ascending=[True, False]).reset_index(drop=True)


def generate_insights(df):
    """Plain-English sentences that explain the numbers."""
    k = overall_kpis(df)
    cats = category_summary(df)
    wk = weekday_vs_weekend(df)
    alerts = budget_check(df)
    cur = config.CURRENCY
    insights = []

    top = cats.iloc[0]
    insights.append(f"{top['category']} is the biggest expense: {cur} {top['total']:,.0f} "
                    f"({top['share_pct']:.1f}% of all spending).")

    non_rent = cats[cats["category"] != "Rent"]
    if not non_rent.empty:
        r = non_rent.iloc[0]
        insights.append(f"Ignoring fixed rent, the biggest flexible spend is {r['category']} "
                        f"at {cur} {r['total']:,.0f}.")

    if wk["weekend"] > wk["weekday"]:
        more = (wk["weekend"] / wk["weekday"] - 1) * 100
        insights.append(f"Weekends cost more: {cur} {wk['weekend']:,.0f} per day versus "
                        f"{cur} {wk['weekday']:,.0f} on weekdays ({more:.0f}% higher).")
    else:
        insights.append("Weekday spending is as high as weekend spending.")

    over = alerts[alerts["status"] == "OVER BUDGET"]
    if over.empty:
        insights.append("No category went over its monthly budget.")
    else:
        worst = over.sort_values("over_by", ascending=False).iloc[0]
        insights.append(f"{len(over)} category-month(s) went over budget. The largest overspend "
                        f"was {worst['category']} in {worst['month']} by {cur} {worst['over_by']:,.0f}.")

    monthly = monthly_summary(df)
    full = monthly[~monthly["is_partial"]]
    if not full.empty:
        best = full.loc[full["savings"].idxmax()]
        insights.append(f"Best savings month: {best['month']} "
                        f"({cur} {best['savings']:,.0f} saved, {best['savings_rate_pct']:.1f}% of income).")
    return insights
