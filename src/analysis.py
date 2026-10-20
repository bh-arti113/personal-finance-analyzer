
import pandas as pd
import numpy as np


def split_transactions(df):
    """Separate income, expenses, and outgoing transfers."""
    income = df[df["income_expense"] == "Income"].copy()
    expenses = df[df["income_expense"] == "Expense"].copy()
    transfers = df[df["income_expense"].str.strip().str.lower() == "transfer-out"].copy()

    return income, expenses, transfers


def financial_summary(df):
    """Calculate top-level financial metrics."""
    income, expenses, transfers = split_transactions(df)

    total_income = income["amount"].sum()
    total_expenses = expenses["amount"].sum()
    total_transfers = transfers["amount"].sum()

    net_flow = total_income - total_expenses

    net_rate = (
        net_flow / total_income * 100
        if total_income > 0 else np.nan
    )

    return pd.DataFrame({
        "Metric": [
            "Total Income",
            "Total Expenses",
            "Transfer-Out Total",
            "Income Minus Expenses",
            "Indicative Net Rate (%)",
            "Transaction Count"
        ],
        "Value": [
            total_income,
            total_expenses,
            total_transfers,
            net_flow,
            net_rate,
            len(df)
        ]
    })


def monthly_analysis(df):
    """Summarize income, expenses, and transfers by month."""
    data = df.copy()
    data["transaction_date"] = pd.to_datetime(
        data["transaction_date"], errors="coerce"
    )
    data = data.dropna(subset=["transaction_date", "amount"])
    data["month"] = data["transaction_date"].dt.to_period("M")

    monthly = {}

    for transaction_type, column_name in [
        ("Income", "Income"),
        ("Expense", "Expenses"),
        ("Transfer-out", "Transfer-Out")
    ]:
        subset = data[data["income_expense"].str.strip().str.lower() == transaction_type.lower()]
        monthly[column_name] = subset.groupby("month")["amount"].sum()

    result = pd.DataFrame(monthly).fillna(0).sort_index()
    result["Net Flow"] = result["Income"] - result["Expenses"]

    return result


def category_analysis(df):
    """Calculate spending totals and averages by expense category."""
    expenses = df[df["income_expense"] == "Expense"].copy()

    result = expenses.groupby("category")["amount"].agg(
        total_spend="sum",
        average_transaction="mean",
        transaction_count="count"
    ).sort_values("total_spend", ascending=False)

    total = expenses["amount"].sum()

    result["share_of_expenses_pct"] = (
        result["total_spend"] / total * 100
        if total > 0 else 0
    )

    return result


def payment_mode_analysis(df):
    """Summarize expense spending by payment mode."""
    expenses = df[df["income_expense"] == "Expense"]

    return expenses.groupby("mode")["amount"].agg(
        total_spend="sum",
        transaction_count="count",
        average_transaction="mean"
    ).sort_values("total_spend", ascending=False)


def detect_unusual_expenses(df):
    """Flag unusually large expenses using the IQR method."""
    expenses = df[df["income_expense"] == "Expense"].copy()

    if len(expenses) < 4:
        return expenses.iloc[0:0].copy()

    q1 = expenses["amount"].quantile(0.25)
    q3 = expenses["amount"].quantile(0.75)
    upper_limit = q3 + 1.5 * (q3 - q1)

    return expenses[expenses["amount"] > upper_limit].sort_values(
        "amount", ascending=False
    )


def generate_insights(df):
    """Generate basic rule-based financial insights."""
    income, expenses, transfers = split_transactions(df)

    total_income = income["amount"].sum()
    total_expenses = expenses["amount"].sum()
    total_transfers = transfers["amount"].sum()

    insights = [
        f"Recorded income: INR {total_income:,.2f}.",
        f"Recorded expenses: INR {total_expenses:,.2f}.",
        f"Outgoing transfers: INR {total_transfers:,.2f}.",
        (
            f"Income minus recorded expenses: "
            f"INR {total_income - total_expenses:,.2f}."
        )
    ]

    categories = category_analysis(df)

    if not categories.empty:
        top_category = categories.index[0]
        top_amount = categories.iloc[0]["total_spend"]

        insights.append(
            f"Largest expense category: {top_category} "
            f"(INR {top_amount:,.2f})."
        )

    unusual = detect_unusual_expenses(df)
    insights.append(
        f"{len(unusual)} expense transactions flagged for review."
    )

    return insights
