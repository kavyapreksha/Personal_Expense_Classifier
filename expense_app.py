import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from sqlalchemy import create_engine, Table, Column, Integer, Float, String, Date, MetaData

from modules.categorizer import categorize

# --- Constants ---
DB_PATH = "data/expenses.db"
TABLE_NAME = "expenses"

# --- Setup SQLAlchemy engine and metadata ---
engine = create_engine(f"sqlite:///{DB_PATH}")
metadata = MetaData()

# --- Define or reflect expenses table ---
expenses_table = Table(
    TABLE_NAME,
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('Date', Date, nullable=False),
    Column('Description', String, nullable=False),
    Column('Amount', Float, nullable=False),
    Column('Type', String, nullable=False),
    Column('Category', String, nullable=False),
)

metadata.create_all(engine)

# --- Load data from DB ---
@st.cache_data(ttl=600)
def load_expenses():
    with engine.connect() as conn:
        df = pd.read_sql_table(TABLE_NAME, conn)
    return df

# --- Insert new expense into DB ---
def add_expense(date, description, amount, type_, category):
    with engine.begin() as conn:
        conn.execute(
            expenses_table.insert().values(
                Date=date,
                Description=description,
                Amount=amount,
                Type=type_,
                Category=category,
            )
        )

# --- Main app ---
def main():
    st.set_page_config(page_title="Expense Categorizer & Analyzer", layout="centered")
    st.title("💰 Personal Expense Categorizer (Auto-Save Database)")

    # --- CSV Upload and ingest ---
    with st.expander("⬆️ Upload Expenses CSV (optional)"):
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file and st.button("Ingest Data into Database"):
            csv_df = pd.read_csv(uploaded_file)
            if not {'Date', 'Description', 'Amount'}.issubset(csv_df.columns):
                st.error("CSV must contain at least 'Date', 'Description', and 'Amount' columns.")
            else:
                csv_df['Date'] = pd.to_datetime(csv_df['Date']).dt.date
                csv_df['Category'] = csv_df['Description'].apply(categorize)
                # You can add default 'Type' column if missing or set it
                if 'Type' not in csv_df.columns:
                    csv_df['Type'] = 'Debit'  # or as you prefer
                csv_df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
                st.success("CSV data ingested into database successfully!")

    # --- Load current data ---
    df = load_expenses()

    if df.empty:
        st.info("No data found. Upload a CSV or add a new expense entry to get started.")
        data_available = False
    else:
        data_available = True
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year-Month'] = df['Date'].dt.to_period('M').astype(str)

    # --- Add new expense entry ---
    with st.expander("➕ Add a New Expense Entry"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_date = st.date_input("Date", value=datetime.today())
        with col2:
            new_desc = st.text_input("Description")
        with col3:
            new_amt = st.number_input("Amount", min_value=0.01, format="%.2f")
        new_type = st.selectbox("Type", ["Debit", "Credit"])

        if st.button("Add Expense"):
            if not new_desc.strip():
                st.error("Description cannot be empty.")
            elif new_amt <= 0:
                st.error("Amount must be greater than zero.")
            else:
                new_category = categorize(new_desc)
                add_expense(new_date, new_desc.strip(), float(new_amt), new_type, new_category)
                st.success("✅ Expense added to database.")
                st.experimental_rerun()

    if data_available:
        # Refresh data after possible new entry
        df = load_expenses()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year-Month'] = df['Date'].dt.to_period('M').astype(str)

        # --- Sidebar month filter ---
        st.sidebar.header("📅 Filter by Month")
        months = sorted(df['Year-Month'].unique(), reverse=True)
        selected_month = st.sidebar.selectbox("Select month", months)

        filtered_df = df[df['Year-Month'] == selected_month]

        st.subheader(f"📄 Categorized Expenses for {selected_month}")
        st.dataframe(filtered_df.sort_values('Date'), use_container_width=True)

        # --- Expense summary ---
        cat_summary = filtered_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)

        st.subheader(f"💸 Expense Summary by Category for {selected_month}")
        st.dataframe(cat_summary)

        if not cat_summary.empty:
            max_cat = cat_summary.idxmax()
            max_amt = cat_summary.max()
            st.markdown(f"🤑 **Highest Spending Category:** `{max_cat}` — ₹{max_amt:,.2f}")

        # --- Pie chart ---
        st.subheader("📊 Spending Distribution by Category")
        fig = px.pie(
            names=cat_summary.index,
            values=cat_summary.values,
            title=f'Category Pie Chart – {selected_month}',
            hole=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Download all data ---
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Data as CSV",
            data=csv_data,
            file_name="all_expenses_database.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
