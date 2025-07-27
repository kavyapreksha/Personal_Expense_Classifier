from sqlalchemy import create_engine, Table, Column, Integer, Float, String, Date, MetaData

DB_NAME = "expenses.db"
TABLE_NAME = "expenses"
engine = create_engine(f"sqlite:///{DB_NAME}")
metadata = MetaData()

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

def insert_expense(date, desc, amount, exp_type, category):
    with engine.begin() as conn:
        conn.execute(
            expenses_table.insert(),
            {"Date": date, "Description": desc, "Amount": amount, "Type": exp_type, "Category": category}
        )

def bulk_insert_expenses(df):
    # df: pandas DataFrame with columns matching table (no id needed)
    with engine.begin() as conn:
        conn.execute(expenses_table.insert(), df.to_dict(orient='records'))

def load_data_as_df():
    import pandas as pd
    df = pd.read_sql_table(TABLE_NAME, engine)
    return df
