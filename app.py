
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Make the src folder importable
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from analysis import (
    financial_summary,
    monthly_analysis,
    category_analysis,
    payment_mode_analysis,
    detect_unusual_expenses,
    generate_insights,
)

st.set_page_config(
    page_title="Personal Finance Analyzer",
    page_icon="💰",
    layout="wide",
)

st.title("💰 Personal Finance Analyzer")
st.caption("Understand your income, expenses, and financial activity.")

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

st.sidebar.header("Transaction Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a cleaned transaction CSV",
    type=["csv"],
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    processed_dir = PROJECT_DIR / "data" / "processed"
    possible_files = [
        processed_dir / "transactions_clean.csv",
        PROJECT_DIR / "data" / "transactions_clean.csv",
    ]

    default_file = next(
        (path for path in possible_files if path.exists()),
        None,
    )

    if default_file is None:
        st.info(
            "Upload your cleaned transaction CSV using the sidebar "
            "to begin. The dashboard expects the standardized columns "
            "used by your analysis module."
        )
        st.stop()

    df = pd.read_csv(default_file)
    st.sidebar.success(f"Loaded: {default_file.name}")

# Normalize column names and transaction labels
df.columns = df.columns.str.strip().str.lower()

required_columns = {
    "transaction_date",
    "amount",
    "income_expense",
    "category",
    "mode",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error(
        "The uploaded file is missing required columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"], errors="coerce"
)
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["income_expense"] = (
    df["income_expense"].astype("string").str.strip()
)

df = df.dropna(
    subset=["transaction_date", "amount", "income_expense"]
).copy()

if df.empty:
    st.error("No valid transactions were found in this CSV.")
    st.stop()

# --------------------------------------------------
# FILTERS
# --------------------------------------------------


st.sidebar.subheader("Filters")

min_date = df["transaction_date"].min().date()
max_date = df["transaction_date"].max().date()

date_range = st.sidebar.date_input(
    "Transaction date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Apply the selected date range
if isinstance(date_range, (tuple, list)) and len(date_range) > 0:
    start_date = date_range[0]
    end_date = date_range[-1]

    df = df[
        df["transaction_date"].dt.date.between(start_date, end_date)
    ].copy()

# Stop safely if the date filter returns no rows
if df.empty:
    st.warning("No transactions match these filters.")
    st.stop()

categories = sorted(
    df.loc[
        df["income_expense"].astype(str).str.strip().str.lower() == "expense",
        "category"
    ].dropna().astype(str).unique()
)

selected_categories = st.sidebar.multiselect(
    "Expense categories",
    options=categories,
    default=categories,
)

# Keep income and transfers visible; filter only expenses by category
transaction_type = (
    df["income_expense"].astype(str).str.strip().str.lower()
)

is_not_expense = transaction_type != "expense"
is_selected_category = df["category"].astype(str).isin(selected_categories)

df = df[is_not_expense | is_selected_category].copy()

if df.empty:
    st.warning("No transactions match these filters.")
    st.stop()


# --------------------------------------------------
# FINANCIAL SUMMARY
# --------------------------------------------------

st.header("Financial Overview")

summary = financial_summary(df)
summary_values = dict(zip(summary["Metric"], summary["Value"]))

income = summary_values["Total Income"]
expenses = summary_values["Total Expenses"]
transfers = summary_values["Transfer-Out Total"]
net_flow = summary_values["Income Minus Expenses"]
net_rate = summary_values["Indicative Net Rate (%)"]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Recorded Income", f"₹{income:,.2f}")
col2.metric("Recorded Expenses", f"₹{expenses:,.2f}")
col3.metric("Income − Expenses", f"₹{net_flow:,.2f}")
col4.metric("Outgoing Transfers", f"₹{transfers:,.2f}")

st.caption(
    f"Indicative net rate: {net_rate:.2f}%"
    if pd.notna(net_rate)
    else "Indicative net rate unavailable."
)
st.caption(
    "Income minus expenses is not necessarily actual savings or "
    "account balance. Transfers are reported separately."
)


# --------------------------------------------------
# MONTHLY ANALYSIS
# --------------------------------------------------

st.header("Monthly Trends")

monthly = monthly_analysis(df)

if not monthly.empty:
    # Convert the monthly index into readable labels
    monthly_display = monthly.copy()
    monthly_display.index = monthly_display.index.astype(str)
    monthly_display.index.name = "Month"

    st.subheader("Income vs. Expenses")
    st.line_chart(monthly_display[["Income", "Expenses"]])

    st.subheader("Monthly Net Flow")
    st.bar_chart(monthly_display[["Net Flow"]])

    with st.expander("View monthly data"):
        st.dataframe(monthly_display, use_container_width=True)

else:
    st.info("There isn't enough valid date information for monthly trends.")


# --------------------------------------------------
# CATEGORY AND PAYMENT MODE
# --------------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Spending by Category")
    category_data = category_analysis(df)

    if not category_data.empty:
        st.bar_chart(category_data["total_spend"].head(10))
        st.dataframe(
            category_data.head(10),
            use_container_width=True,
        )
    else:
        st.info("No expense transactions in this selection.")

with right:
    st.subheader("Spending by Payment Mode")
    mode_data = payment_mode_analysis(df)

    if not mode_data.empty:
        st.bar_chart(mode_data["total_spend"])
        st.dataframe(mode_data, use_container_width=True)
    else:
        st.info("No expense transactions in this selection.")

# --------------------------------------------------
# UNUSUAL EXPENSES
# --------------------------------------------------

st.header("Unusual Expenses for Review")

unusual = detect_unusual_expenses(df)

st.caption(
    "These transactions exceed a statistical threshold. "
    "They are not automatically errors or evidence of fraud."
)

if unusual.empty:
    st.success("No transactions were flagged in this selection.")
else:
    st.write(f"Transactions flagged: {len(unusual)}")
    st.dataframe(
        unusual,
        use_container_width=True,
        hide_index=True,
    )

# --------------------------------------------------
# AUTOMATED INSIGHTS
# --------------------------------------------------

st.header("Automated Financial Insights")

for insight in generate_insights(df):
    st.markdown(f"- {insight}")

# --------------------------------------------------
# DOWNLOADS
# --------------------------------------------------

st.header("Download Analysis")

download_col1, download_col2 = st.columns(2)

with download_col1:
    st.download_button(
        "Download filtered transactions",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_transactions.csv",
        mime="text/csv",
    )

with download_col2:
    st.download_button(
        "Download financial summary",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name="financial_summary.csv",
        mime="text/csv",
    )
