"""
visualize.py - the four charts. Each plot_* function RETURNS a matplotlib
Figure, so the same code works for saving PNG files and for Streamlit.
"""
import matplotlib

matplotlib.use("Agg")  # draw without opening a window (works on any machine)
import matplotlib.pyplot as plt
import seaborn as sns

from src import analysis, config

sns.set_theme(style="whitegrid")
CUR = config.CURRENCY


def plot_category_bar(df):
    """Chart 1: total spending per category (horizontal bar)."""
    data = analysis.category_summary(df)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.barplot(data=data, x="total", y="category", hue="category",
                palette="viridis", legend=False, ax=ax)
    for i, row in data.iterrows():
        ax.text(row["total"], i, f"  {CUR} {row['total']:,.0f}", va="center", fontsize=9)
    ax.set_title("Category-wise Spending", fontsize=14, weight="bold")
    ax.set_xlabel(f"Total spent ({CUR})")
    ax.set_ylabel("")
    ax.set_xlim(0, data["total"].max() * 1.2)
    fig.tight_layout()
    return fig


def plot_monthly_line(df):
    """Chart 2: total spending per month (line). Partial months are marked."""
    data = analysis.monthly_summary(df)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(data["month"], data["total_spending"], marker="o", linewidth=2.5, color="#1f77b4")
    for _, row in data.iterrows():
        label = f"{CUR} {row['total_spending']:,.0f}"
        if row["is_partial"]:
            label += "\n(partial month)"
        ax.annotate(label, (row["month"], row["total_spending"]),
                    textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)
    ax.axhline(config.MONTHLY_INCOME, color="red", linestyle="--", linewidth=1,
               label=f"Assumed income ({CUR} {config.MONTHLY_INCOME:,})")
    ax.set_title("Monthly Spending Trend", fontsize=14, weight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel(f"Total spent ({CUR})")
    ax.set_ylim(0, max(data["total_spending"].max(), config.MONTHLY_INCOME) * 1.2)
    ax.legend(loc="lower right")
    fig.tight_layout()
    return fig


def plot_payment_pie(df):
    """Chart 3: share of spending by payment method (pie)."""
    data = analysis.payment_summary(df)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(data["total"], labels=data["payment_method"], autopct="%1.1f%%",
           startangle=90, colors=sns.color_palette("pastel"),
           wedgeprops={"edgecolor": "white"})
    ax.set_title("Spending by Payment Method", fontsize=14, weight="bold")
    fig.tight_layout()
    return fig


def plot_daily_trend(df):
    """
    Chart 4: everyday spending per day, with a 7-day moving average.
    Rent is left out because one Rs. 12,000 payment would hide the daily pattern.
    """
    data = analysis.daily_spending(df[df["category"] != "Rent"])
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(data["date"], data["total"], color="#9ecae1", label="Daily total", width=1.0)
    ax.plot(data["date"], data["moving_avg_7d"], color="#d62728",
            linewidth=2.2, label="7-day moving average")
    ax.set_title("Daily Spending Trend (excluding rent)", fontsize=14, weight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Spent ({CUR})")
    ax.set_ylim(0, data["total"].max() * 1.3)  # headroom so the legend hides nothing
    ax.legend(loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


CHARTS = {
    "01_category_spending_bar.png": plot_category_bar,
    "02_monthly_spending_trend.png": plot_monthly_line,
    "03_payment_method_pie.png": plot_payment_pie,
    "04_daily_spending_trend.png": plot_daily_trend,
}


def save_all_charts(df, folder=None):
    """Draw all four charts and save them as PNG files. Returns the paths."""
    folder = folder or config.IMAGE_DIR
    folder.mkdir(parents=True, exist_ok=True)
    saved = []
    for filename, plot_function in CHARTS.items():
        fig = plot_function(df)
        path = folder / filename
        fig.savefig(path, dpi=150)
        plt.close(fig)
        saved.append(path)
    return saved
