"""
report.py - saves the analysis results as CSV files and one readable
text report.
"""
from datetime import datetime

from src import analysis, config

CUR = config.CURRENCY


def save_tables(df, folder=None):
    """Save every summary table to outputs/ as CSV. Returns the paths."""
    folder = folder or config.OUTPUT_DIR
    folder.mkdir(parents=True, exist_ok=True)
    tables = {
        "cleaned_expenses.csv": df,
        "category_summary.csv": analysis.category_summary(df),
        "monthly_summary.csv": analysis.monthly_summary(df),
        "payment_summary.csv": analysis.payment_summary(df),
        "daily_spending.csv": analysis.daily_spending(df),
        "budget_check.csv": analysis.budget_check(df),
    }
    paths = []
    for name, table in tables.items():
        path = folder / name
        table.to_csv(path, index=False)
        paths.append(path)
    return paths


def build_text_report(df, cleaning_log):
    """Return the full text report as one string."""
    k = analysis.overall_kpis(df)
    cats = analysis.category_summary(df)
    pays = analysis.payment_summary(df)
    monthly = analysis.monthly_summary(df)
    budget = analysis.budget_check(df)
    over = budget[budget["status"] == "OVER BUDGET"]
    line = "=" * 62

    out = [line, "PERSONAL EXPENSE TRACKER - SUMMARY REPORT", line,
           f"Generated on : {datetime.now():%Y-%m-%d %H:%M}",
           f"Data period  : {k['first_date']:%Y-%m-%d} to {k['last_date']:%Y-%m-%d} ({k['n_days']} days)",
           "", "DATA CLEANING"]
    for key, value in cleaning_log.items():
        out.append(f"  {key.replace('_', ' ').capitalize():<32}: {value}")

    out += ["", "KEY NUMBERS",
            f"  Total spending         : {CUR} {k['total_spending']:,.2f}",
            f"  Number of transactions : {k['n_transactions']}",
            f"  Average transaction    : {CUR} {k['avg_transaction']:,.2f}",
            f"  Average daily spending : {CUR} {k['avg_daily_spending']:,.2f}",
            f"  Highest category       : {k['top_category']} ({CUR} {k['top_category_amount']:,.2f})",
            f"  Biggest single expense : {CUR} {k['biggest_expense_amount']:,.2f} "
            f"({k['biggest_expense_desc']}, {k['biggest_expense_date']:%Y-%m-%d})",
            f"  Busiest spending day   : {k['busiest_day']:%Y-%m-%d} ({CUR} {k['busiest_day_amount']:,.2f})",
            "", "SPENDING BY CATEGORY"]
    for _, r in cats.iterrows():
        out.append(f"  {r['category']:<20} {CUR} {r['total']:>10,.2f}   {r['share_pct']:>5.1f}%")

    out += ["", "SPENDING BY PAYMENT METHOD"]
    for _, r in pays.iterrows():
        out.append(f"  {r['payment_method']:<20} {CUR} {r['total']:>10,.2f}   {r['share_pct']:>5.1f}%")

    out += ["", "MONTHLY SUMMARY"]
    for _, r in monthly.iterrows():
        if r["is_partial"]:
            tail = f"partial month ({r['days_covered']} days of data)"
        else:
            tail = f"saved {CUR} {r['savings']:,.2f} ({r['savings_rate_pct']:.1f}%)"
        out.append(f"  {r['month']}  spent {CUR} {r['total_spending']:>10,.2f}   {tail}")

    out += ["", "BUDGET ALERTS"]
    if over.empty:
        out.append("  No budget limits were exceeded.")
    else:
        for _, r in over.iterrows():
            out.append(f"  {r['month']}  {r['category']:<18} spent {CUR} {r['spent']:>9,.2f} "
                       f"/ budget {CUR} {r['budget']:>9,.2f}  (over by {CUR} {r['over_by']:,.2f})")

    out += ["", "INSIGHTS"]
    out += [f"  - {text}" for text in analysis.generate_insights(df)]
    out += ["", "Note: all data in this project is synthetic and for learning only.", line]
    return "\n".join(out)


def save_text_report(df, cleaning_log, folder=None):
    """Write the text report to reports/summary_report.txt."""
    folder = folder or config.REPORT_DIR
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "summary_report.txt"
    path.write_text(build_text_report(df, cleaning_log), encoding="utf-8")
    return path
