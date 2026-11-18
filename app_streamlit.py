"""
app_streamlit.py - OPTIONAL interactive dashboard.

Run with:   streamlit run app_streamlit.py
(needs:     pip install streamlit)
"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src import analysis, config, data_generator, data_loader, visualize

CUR = config.CURRENCY

st.set_page_config(page_title="Personal Expense Tracker", layout="wide")
st.title("Personal Expense Tracker")
st.caption("Demo uses synthetic data. Upload your own CSV in the sidebar "
           "(columns: date, category, amount, payment_method, description).")


@st.cache_data
def load_demo_data():
    """Load the sample CSV (creating it first if it does not exist)."""
    if not config.DEFAULT_CSV.exists():
        data_generator.create_sample_csv()
    return data_loader.load_expenses()


# ---------- 1. Choose the data source ----------
uploaded = st.sidebar.file_uploader("Upload expenses CSV", type="csv")
if uploaded is not None:
    try:
        df, log = data_loader.clean_expenses(pd.read_csv(uploaded))
    except Exception as error:  # show a friendly message instead of a crash
        st.error(f"Could not read that file: {error}")
        st.stop()
else:
    df, log = load_demo_data()

# ---------- 2. Sidebar filters ----------
month_choice = st.sidebar.selectbox("Month", ["All months"] + sorted(df["month"].unique()))
category_choice = st.sidebar.multiselect(
    "Categories", sorted(df["category"].unique()), default=sorted(df["category"].unique()))

view = df[df["category"].isin(category_choice)]
if month_choice != "All months":
    view = view[view["month"] == month_choice]

if view.empty:
    st.warning("No expenses match these filters.")
    st.stop()

# ---------- 3. Key numbers ----------
k = analysis.overall_kpis(view)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total spending", f"{CUR} {k['total_spending']:,.0f}")
c2.metric("Average per day", f"{CUR} {k['avg_daily_spending']:,.0f}")
c3.metric("Transactions", k["n_transactions"])
c4.metric("Top category", k["top_category"])

# ---------- 4. Charts ----------
left, right = st.columns(2)
for column, plot_function in [(left, visualize.plot_category_bar),
                              (right, visualize.plot_monthly_line),
                              (left, visualize.plot_payment_pie),
                              (right, visualize.plot_daily_trend)]:
    figure = plot_function(view)
    column.pyplot(figure)
    plt.close(figure)

# ---------- 5. Insights, budget check and cleaning log ----------
st.subheader("Insights")
for sentence in analysis.generate_insights(view):
    st.write("- " + sentence)

st.subheader("Budget check")
st.dataframe(analysis.budget_check(view), use_container_width=True)

with st.expander("Data cleaning log"):
    st.json(log)
