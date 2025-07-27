import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, Date, MetaData
from datetime import datetime

DB_NAME = "expenses.db"
TABLE_NAME = "expenses"
engine = create_engine(f"sqlite:///{DB_NAME}")
metadata = MetaData()

# --- Define table (runs only once) ---
expenses_table = Table(
    TABLE_NAME, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('Date', Date, nullable=False),
    Column('Description', String, nullable=False),
    Column('Amount', Float, nullable=False),
    Column('Type', String, nullable=False),
    Column('Category', String, nullable=False)
)

metadata.create_all(engine)

# --- Categorization function ---
def categorize(description):
    desc = str(description).lower()
    if any(x in desc for x in ['pharmacy', 'medical', 'doctor', 'hospital', 'medicine']):
        return 'Medical'
    elif any(x in desc for x in ['fruit', 'vegetables', 'big bazaar', 'grocery']):
        return 'Groceries'
    elif any(x in desc for x in ['netflix', 'youtube', 'book', 'headphones', 'udemy']):
        return 'Subscriptions & Books'
    elif any(x in desc for x in ['train', 'taxi', 'ola', 'uber', 'auto', 'bus','rapido']):
        return 'Transportation'
    elif any(x in desc for x in ['lunch', 'dinner', 'snack', 'zomato', 'starbucks', 'ice cream', 'mcdonald', 'pizza']):
        return 'Food & Dining'
    elif any(x in desc for x in ['petrol', 'diesel', 'cng']):
        return 'Fuel'
    elif 'rent' in desc:
        return 'Rent'
    elif 'recharge' in desc:
        return 'Mobile Recharge'
    elif any(x in desc for x in ['myntra', 'jeans', 't-shirt', 'h&m', 'shirt', 'clothing']):
        return 'Clothing'
    else:
        return 'Others'

st.set_page_config(page_title="Expense Categorizer & Analyzer", layout="centered")
st.title("💰 Personal Expense Categorizer (Auto-Save Database)")

# --- Initial CSV Upload ---
with st.expander("⬆️ Upload Expenses CSV (first time only, optional)"):
    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded and st.button("Ingest Data into Database"):
        csv_df = pd.read_csv(uploaded)
        csv_df['Date'] = pd.to_datetime(csv_df['Date'])
        csv_df['Category'] = csv_df['Description'].apply(categorize)
        csv_df['Date'] = csv_df['Date'].dt.date  # For SQLite compatibility
        csv_df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
        st.success('Data uploaded to database.')

# --- Load data from DB ---
df = pd.read_sql_table(TABLE_NAME, engine)
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year-Month'] = df['Date'].dt.to_period('M').astype(str)

# --- Add New Expense Entry ---
# --- Add a New Expense Entry ---
with st.expander("➕ Add a New Expense Entry"):
    col1, col2, col3 = st.columns(3)
    with col1:
        new_date = st.date_input("Date", value=datetime.today())
    with col2:
        new_desc = st.text_input("Description")
    with col3:
        new_amt = st.number_input("Amount", min_value=0.01, format="%.2f")
    
    new_type = st.selectbox("Type", ["Debit", "Credit"])

    # ✅ Properly indented block for adding an expense
    if st.button("Add Expense"):
        if new_desc and new_amt:
            category = categorize(new_desc)
            
            with engine.begin() as conn:
                conn.execute(
                    expenses_table.insert(),
                    {
                        "Date": new_date,
                        "Description": new_desc,
                        "Amount": float(new_amt),
                        "Type": new_type,
                        "Category": category
                    }
                )
            st.success("✅ Expense added (saved to database).")
            st.rerun()


# --- Monthly Filter and Analysis ---
if not df.empty:
    # Refresh data after entry
    df = pd.read_sql_table(TABLE_NAME, engine)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year-Month'] = df['Date'].dt.to_period('M').astype(str)

    st.sidebar.header("📅 Filter by Month")
    month_list = sorted(df['Year-Month'].unique(), reverse=True)
    selected_month = st.sidebar.selectbox("Select a month", month_list)
    filtered_df = df[df['Year-Month'] == selected_month]

    st.subheader(f"📄 Categorized Expenses for {selected_month}")
    st.dataframe(filtered_df.sort_values('Date'), use_container_width=True)

    cat_summary = filtered_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    st.subheader(f"💸 Expense Summary by Category for {selected_month}")
    st.dataframe(cat_summary)

    if not cat_summary.empty:
        max_cat = cat_summary.idxmax()
        max_amt = cat_summary.max()
        st.markdown(f"🤑 **Highest Spending Category:** `{max_cat}` — ₹{max_amt:,.2f}")

    st.subheader("📊 Spending Distribution by Category")
    fig = px.pie(
        names=cat_summary.index,
        values=cat_summary.values,
        title=f'Category Pie Chart – {selected_month}',
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "📥 Download All Data as CSV",
        data=df.to_csv(index=False),
        file_name="all_expenses_database.csv",
        mime="text/csv"
    )
else:
    st.info("No data found. Upload your CSV or add a new expense to begin.")
