# 📦 Inventory Management System

A web-based **Inventory Management System** built with **Python** and **Streamlit**, backed by a **PostgreSQL** database. It provides a clean, multi-page dashboard to manage inventory records, employee details, and reports — all from one centralized interface.

---

## 🚀 Features

- 🏠 **Home Dashboard** — Quick access cards and system overview
- 📦 **Inventory Management** — Add, update, search, and track product stock
- 👨‍💼 **Employee Management** — Manage employee records and department details
- 📊 **Reports & Analytics** — View report summary
- 🔍 **Search & Filters** — Quickly locate records across modules
- ✅ **Status Tracking** — Monitor inventory and employee status in real time

---

## 🛠️ Tech Stack

| Layer       | Technology  |
|-------------|-------------|
| Frontend    | Streamlit   |
| Backend     | Python      |
| Database    | PostgreSQL  |
| DB Driver   | psycopg2    |

---

## 📁 Project Structure

```
INVENTORY_MGT/
├── Inventory.py                    # Main — Inventory dashboard
├── db_connection.py                # PostgreSQL connection utility
├── test.py                         # Testing script (gitignored)
├── .env                            # Environment variables (gitignored)
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
|
└── __pycache__/                    # Python bytecode cache (gitignored)
```
---

## ⚙️ Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL installed and running
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/ishaan-ranjan16/inventory.git
cd inventory
```

### 2. Install Dependencies

```bash
pip install streamlit psycopg2 python-dotenv
```

### 3. Set Up the Database

Create a PostgreSQL database named `inventory_db`:

```sql
CREATE DATABASE inventory_db;
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_NAME=inventory_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

### 5. Run the Application

```bash
streamlit run Inventory.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📸 Pages Overview

| Page              | Description                              |
|-------------------|------------------------------------------|
| 📦 Inventory      | Invnetory Dashboard - Add and manage inventory , view and update records with download option.|
<!-- | 👨‍💼 Employees      | View and update employee records         |
| 📁 Reports        | Analytics and report summaries           | -->

---

## 📄 License

This project is currently under development. Feel free to go through it.

---

