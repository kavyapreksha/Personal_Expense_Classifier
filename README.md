# 💸 Expense Tracker App

A modular, user-friendly Streamlit application for tracking, categorizing, and analyzing your personal expenses.  
All data is saved locally using SQLite, ensuring privacy and persistence without requiring any cloud or server setup.

---

## 🚀 Features

- Upload historical expenses from a CSV file (one-time import)  
- Add new expenses with date, description, amount, and type via an intuitive UI  
- Automatic categorization of expenses based on description keywords  
- Filter expenses by month and analyze spending category-wise  
- Interactive pie chart visualization for better spending insights  
- Persistent local database (SQLite) to save all your data automatically  
- Download the entire expense database as a CSV anytime  
- Modular code structure for easy maintenance and customization

---

## 📁 Project Structure
```
expense_tracker_app/
├── app.py # Main Streamlit UI and app orchestration
├── categorizer.py # Expense categorization logic
├── db_utils.py # SQLite database utility functions
├── requirements.txt # Python dependencies list
├── .gitignore # Specifies files/folders to ignore in Git version control
└── README.md # This README file you are reading now
```

---

## ⚙️ Installation & Setup

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/) (optional, for version control)

### Steps

1. **Clone the repository (or download the source code):**

    ```
    git clone https://github.com/<your-username>/expense_tracker_app.git
    cd expense_tracker_app
    ```

2. **Install required Python packages:**

    ```
    pip install -r requirements.txt
    ```

3. **Run the Streamlit app:**

    ```
    streamlit run app.py
    ```

---

## 📖 Usage Guide

### 1. Upload Existing Expenses (One-time import)

- Use the **“Upload Expenses CSV”** section on the app page.
- Your CSV file must have the following columns:  
  `Date`, `Description`, `Amount`, `Type`
- Click the button to import and persist your historical data.

### 2. Add New Expense Entries

- Fill out the "Add a New Expense Entry" form in the app with:
  - Date of expense
  - Description (e.g., “Zomato”, “Uber”)
  - Amount
  - Type (Debit or Credit)
- Click **Add Expense** to save it. The app automatically categorizes and stores it in the database.

### 3. Analyze Your Expenses

- Use the **sidebar month filter** dropdown to select the month you want to analyze.
- View:
  - A table of all expenses for that month, categorized.
  - Summary of amounts spent per category.
  - The category with the highest spending.
  - An interactive pie chart to visually understand your spending distribution.

### 4. Download Expense Data

- At any time, download the entire set of your categorized expenses as a CSV file using the provided download button.

---

## 🔒 Data Privacy & Security

- All data is stored locally in a SQLite database file `expenses.db`.
- This file is excluded from version control through `.gitignore` to keep your data secure and private.
- No data leaves your machine unless you explicitly share or upload it.

---

## 🛠 Customization & Development

- **Modify categorization rules:** Edit `categorizer.py` to tweak how expenses are classified.
- **Change database logic:** Update `db_utils.py` for advanced storage or queries.
- **Customize UI:** Adjust `app.py` for new features, UI improvements, or additional filters.

---

## 🤔 Frequently Asked Questions (FAQ)

**Q: Can multiple users use this app on the same machine?**  
A: Currently, the app is designed for single-user use. Multi-user support requires further customization.

**Q: How do I back up my data?**  
A: Simply copy the `expenses.db` file to another location.

**Q: What if my CSV columns don't match?**  
A: Ensure your CSV has exactly the columns: `Date`, `Description`, `Amount`, `Type`. The `Date` should be in a format recognized by pandas.

---

## 📚 Useful Links

- [Streamlit Documentation](https://docs.streamlit.io/)  
- [SQLite Documentation](https://www.sqlite.org/index.html)  
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/14/)

---

## 🙌 Contributing

Pull requests and suggestions are welcome!  
Please keep your additions modular and well-commented.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Happy budgeting and expense tracking! 💰📊
