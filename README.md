<!-- # 📦 Inventory Management System

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

| Layer       | Technology          |
|-------------|---------------------|
| Frontend    | Streamlit           |
| Backend     | Python              |
| Database    | PostgreSQL          |
| DB Driver   | psycopg2            |

---

## 📁 Project Structure

```
inventory/
├── Home.py                # Main entry point — home dashboard page
├── db_connection.py       # PostgreSQL connection utility
├── pages/                 # Streamlit multi-page app pages
│   ├── Inventory.py       # Inventory management page
│   ├── Employees.py       # Employee management page
    ├── Dashboard.py       # Dashboard overview page
│   └── Report.py         # Reports & analytics page
└── __pycache__/           # Python bytecode cache
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
pip install streamlit psycopg2
```

### 3. Set Up the Database

Create a PostgreSQL database named `inventory_db`:

```sql
CREATE DATABASE inventory_db;
```

Then update the credentials in `db_connection.py` to match your local PostgreSQL setup:

```python
conn = psycopg2.connect(
    host="localhost",
    database="inventory_db",
    user="your_username",
    password="your_password",
    port=5432
)
```

> ⚠️ **Note:** Avoid committing plain-text credentials. Consider using environment variables or a `.env` file with `python-dotenv`.

### 4. Run the Application

```bash
streamlit run Home.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📸 Pages Overview

| Page       | Description                                         |
|------------|-----------------------------------------------------|
| 🏠 Home    | Welcome dashboard with quick-access cards           |
| 📦 Inventory | Add and manage products and stock levels          |
| 👨‍💼 Employees | View and update employee records                  |
| 📊 Dashboard | Visualize inventory and employee stats            |
| 📁 Reports   | Analytics and report summaries                    |

---
## 📄 License

This project is currently open source. Feel free to go through it.

--- -->

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
├── Home.py                         # Main entry point — home dashboard
├── db_connection.py                # PostgreSQL connection utility
├── test.py                         # Testing script
├── .env                            # Environment variables (gitignored)
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── pages/                          # Streamlit multi-page app pages
│   ├── 1_Inventory-Section.py      # Inventory management page
│   ├── 2_Employee-Section.py       # Employee management page
│   └── 3_Report.py                 # Reports & analytics page
|
└── __pycache__/                    # Python bytecode cache (gitignored)
```


<!-- ## 📁 Project Structure

```
INVENTORY_MGT/
├── Home.py                         # Main entry point — home dashboard
├── db_connection.py                # PostgreSQL connection utility
├── test.py                         # Testing script
├── .env                            # Environment variables (gitignored)
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── pages/                          # Streamlit multi-page app pages
│   ├── 1_Inventory-Section.py      # Inventory management page
│   ├── 2_Employee-Section.py       # Employee management page
│   ├── 3_Dashboard-T1.py           # Dashboard overview (Type 1)
│   ├── 4_Report.py                 # Reports & analytics page
│   └── 5_Dashboard-T2.py           # Dashboard overview (Type 2)
└── __pycache__/                    # Python bytecode cache (gitignored)
``` -->

<!-- ## 📁 Project Structure -

INVENTORY_MGT/

├── .env                        # Environment variables (gitignored)

├── .gitignore                  # Git ignore rules

├── Home.py                     # Main entry point — home dashboard

├── db_connection.py            # PostgreSQL connection utility

├── README.md                   # Project documentation

├── test.py                     # Testing script

└── pages/                      # Streamlit multi-page app

├── 1_Inventory-Section.py  # Inventory management page

├── 2_Employee-Section.py   # Employee management page

├── 3_Dashboard-T1.py       # Dashboard overview (Type 1)

├── 4_Report.py             # Reports & analytics page

└── 5_Dashboard-T2.py       # Dashboard overview (Type 2) -->

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
streamlit run Home.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📸 Pages Overview

| Page              | Description                              |
|-------------------|------------------------------------------|
| 🏠 Home           | Welcome dashboard with quick-access cards|
| 📦 Inventory      | Add and manage products and stock levels |
| 👨‍💼 Employees    | View and update employee records         |
| 📁 Reports        | Analytics and report summaries           |


<!-- | 📊 Dashboard T1   | Inventory and employee stats (view 1)    |
| 📊 Dashboard T2   | Inventory and employee stats (view 2)    | -->
---

## 📄 License

This project is currently open source. Feel free to go through it.

---

