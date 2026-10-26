# 💰 Personal Finance Analyzer

**Live Demo:** [Try the Personal Finance Analyzer](https://personal-finance-analyzer-5zr6mbejtenuyobv6wzf6f.streamlit.app/)

**Source Code:** [GitHub Repository](https://github.com/bh-arti113/personal-finance-analyzer)

An interactive Python dashboard for exploring income, expenses, transfers, and spending patterns using transaction data.

Built with **Python, Pandas, NumPy, and Streamlit**.

## Overview

The Personal Finance Analyzer turns transaction records into a financial overview with interactive filters, monthly trends, spending breakdowns, unusual-expense flags, and automated insights.

## Features

- **Financial overview** — recorded income, recorded expenses, income minus expenses, outgoing transfers, and an indicative net rate.
- **Interactive filters** — filter transactions by date range and expense category.
- **Monthly trends** — compare income and expenses over time and inspect monthly net flow.
- **Spending analysis** — explore spending by category and payment mode.
- **Unusual-expense review** — flag transactions that exceed a statistical threshold for further inspection.
- **Automated insights** — generate plain-language summaries from the selected transactions.
- **CSV downloads** — export filtered transactions and a financial summary.

> **Important:** Income minus expenses is not necessarily actual savings or an account balance. Transfers are reported separately, and unusual transactions are flagged for review—not automatically classified as errors or fraud.

## Tech Stack

- Python
- Pandas
- NumPy
- Streamlit
- Matplotlib and Seaborn for exploratory analysis and visualizations
- Jupyter Notebook for data exploration and cleaning

## Project Structure

```text
personal-finance-analyzer/
├── app.py
├── requirements.txt
├── data/
│   └── processed/
│       └── transactions_clean.csv   # local data; not committed
├── notebook/
│   ├── 01_data_exploratory.ipynb
│   └── real_data_cleaning.ipynb
├── src/
│   └── analysis.py
├── reports/                         # generated analysis exports
├── .gitignore
└── README.md
```

The exact files in `data/`, `src/`, and `reports/` may vary as the project evolves. Transaction data and generated reports may be kept locally rather than committed to Git.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/bh-arti113/personal-finance-analyzer.git
cd personal-finance-analyzer
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Prepare your transaction data

Run the data-cleaning workflow in the notebook and save your cleaned transaction file locally as:

```text
data/processed/transactions_clean.csv
```

Alternatively, launch the app and upload a cleaned CSV through the sidebar.

The uploaded CSV must include these columns:

- `transaction_date`
- `amount`
- `income_expense`
- `category`
- `mode`

Use consistent transaction labels such as `Income`, `Expense`, and `Transfer-Out`. The app expects standardized, cleaned transaction data; the original household dataset is not included in this repository.

### 5. Run the dashboard

```bash
streamlit run app.py
```

Streamlit will provide a local URL to open in your browser.

## Data and Privacy

- Do not commit personal financial records, credentials, or sensitive information.
- The original external dataset is not bundled with this repository. Obtain it from its source and review the applicable dataset terms before reuse.
- Upload a cleaned CSV with the required columns to explore your own data.
- Use synthetic or anonymized records when sharing screenshots or demonstrations.

## Limitations

- Results depend on the accuracy and consistency of the input data.
- An unusual-expense flag is a statistical review aid, not proof of fraud.
- The indicative net rate is a simple calculation based on recorded income and expenses; it does not account for every aspect of personal finances.

## Future Improvements

- Improve data validation and cleaning feedback.
- Add more detailed merchant and account analysis.
- Expand automated insights and trend comparisons.
- Improve the dashboard's presentation and reporting.

## Author

**bh-arti113**

GitHub: [@bh-arti113](https://github.com/bh-arti113)

---

*This project is for educational and analytical purposes and is not financial advice.*
