import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, Date, MetaData
from sqlalchemy.exc import SQLAlchemyError

from modules.categorizer import categorize

# ---- Database setup ----
DB_PATH = "data/expenses.db"
TABLE_NAME = "expenses"

engine = create_engine(f"sqlite:///{DB_PATH}")
metadata = MetaData()
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

@st.cache_data(ttl=600)
def load_expenses():
    with engine.connect() as conn:
        if engine.dialect.has_table(conn, TABLE_NAME):
            df = pd.read_sql_table(TABLE_NAME, conn)
        else:
            df = pd.DataFrame()
    return df

def add_expense(date, description, amount, type_, category):
    with engine.begin() as conn:
        conn.execute(
            expenses_table.insert().values(
                Date=date,
                Description=description,
                Amount=amount,
                Type=type_,
                Category=category
            )
        )

def ingest_csv_data(csv_df):
    csv_df['Date'] = pd.to_datetime(csv_df['Date']).dt.date
    csv_df['Category'] = csv_df['Description'].apply(categorize)
    if 'Type' not in csv_df.columns:
        csv_df['Type'] = 'Debit'
    csv_df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)

def clear_expenses_table():
    with engine.begin() as conn:
        conn.execute(expenses_table.delete())

# ---- Beautiful, User-Friendly App ----
def main():
    st.set_page_config(page_title="🌈 Expense Dashboard", layout="wide")
    st.title("💸 Personal Monthly Expense Manager")

    st.markdown("""
    <style>
    .big-font {font-size:27px !important;}
    .stButton>button {background-color: #6C63FF; color: white;}
    .stDownloadButton>button {background-color:#4E944F;}
    .sidebar .sidebar-content {background-image: linear-gradient(#e1bee7,#e3f2fd);}
    .stDataFrame {background-color:#f8fafc;}
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.header("📅 Filter By")
    df = load_expenses()
    
    # Sidebar: Year & Month selection
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        years = sorted(df['Date'].dt.year.unique(), reverse=True)
        year = st.sidebar.selectbox("Year", years, format_func=lambda x: f"📅 {x}")
        months = sorted(df[df['Date'].dt.year == year]['Date'].dt.month.unique(), reverse=True)
        month = st.sidebar.selectbox("Month", months, format_func=lambda x: datetime(1900, x, 1).strftime('%B'))
        mask = (df['Date'].dt.year == year) & (df['Date'].dt.month == month)
        filtered_df = df[mask].copy()
        filtered_df['Date'] = filtered_df['Date'].dt.strftime('%Y-%m-%d')
    else:
        filtered_df = pd.DataFrame()

    # ---- Main Layout ----
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### ➕ **Add New Expense**")
        with st.form("add_expense_form", clear_on_submit=True):
            exp_date = st.date_input("Date", value=datetime.today(), format="YYYY-MM-DD")
            description = st.text_input("Description")
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            exp_type = st.selectbox("Type", ["Debit", "Credit"])
            submit = st.form_submit_button("Add Expense", use_container_width=True)
            if submit:
                if not description.strip():
                    st.warning("Please enter a description.")
                elif amount <= 0:
                    st.warning("Amount should be greater than zero.")
                else:
                    try:
                        new_category = categorize(description)
                        add_expense(exp_date, description.strip(), float(amount), exp_type, new_category)
                        st.success("Expense added!")
                        st.cache_data.clear(); st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add expense: {e}")

        st.markdown("#### 📤 **Upload Expenses (CSV)**")
        with st.form("csv_upload_form"):
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
            ingest_now = st.form_submit_button("Ingest CSV To Database", use_container_width=True)
            if uploaded_file and ingest_now:
                try:
                    csv_df = pd.read_csv(uploaded_file)
                    required = {'Date', 'Description', 'Amount'}
                    if not required.issubset(csv_df.columns):
                        st.warning(f"CSV must contain: {', '.join(required)}")
                    else:
                        ingest_csv_data(csv_df)
                        st.success("CSV ingested!")
                        st.cache_data.clear(); st.rerun()
                except Exception as e:
                    st.error(f"CSV ingest failed: {e}")

        st.markdown("#### 🗑️ **Danger Zone**")
        if st.button("Clear All Database", use_container_width=True):
            if st.confirm("Are you sure? This cannot be undone!"):
                clear_expenses_table()
                st.cache_data.clear()
                st.success("Database cleared.")
                st.rerun()

        st.markdown("#### 📥 **Download Data**")
        if not df.empty:
            st.download_button(
                label="Download Full Expenses CSV",
                data=df.to_csv(index=False),
                file_name="expenses_full.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No data to download.")

    with col2:
        st.markdown('<div class="big-font">📋 Monthly Expenses Overview</div>', unsafe_allow_html=True)
        if not filtered_df.empty:
            st.dataframe(filtered_df[['Date', 'Description', 'Amount', 'Type', 'Category']].sort_values('Date'), use_container_width=True)

            cat_sum = filtered_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)

            st.markdown('<div class="big-font">📊 Expenses By Category</div>', unsafe_allow_html=True)
            c1, c2 = st.columns([2, 1.1])
            with c1:
                st.dataframe(cat_sum, use_container_width=True)
                if not cat_sum.empty:
                    st.info(f"Top: `{cat_sum.idxmax()}` : ₹{cat_sum.max():,.2f}")
            with c2:
                if not cat_sum.empty and len(cat_sum) > 0:
                    fig = px.pie(values=cat_sum.values, names=cat_sum.index,
                                 color_discrete_sequence=px.colors.sequential.RdBu,
                                 title=f"Spending by Category ({year}-{month:02d})", hole=0.5)
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses for selected month.")

if __name__ == "__main__":
    main()
