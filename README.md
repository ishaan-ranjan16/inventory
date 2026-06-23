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

--- -->

# 📦 Inventory Management System (INVENTORY_MGT)

A modern, production-style **Inventory Management System** built using **Streamlit**, **Pandas**, and a relational database.
It provides a clean dashboard for managing inventory assets, tracking item lifecycle, and generating exportable reports in PDF and Excel formats.

---

# 📁 Project Structure

```text
INVENTORY_MGT/
│
├── pages/                     # Multi-page Streamlit app (if used)
├── tests/                     # Unit tests
├── __pycache__/              # Python cache (auto-generated)
├── .pytest_cache/            # Pytest cache
│
├── .env                      # Environment variables (DB credentials, secrets)
├── .gitignore
│
├── db_connection.py         # Database connection handler
├── inventory.py             # Main Streamlit dashboard application
├── Inventory-test.py        # Testing / experimental dashboard script
├── test.py                  # Unit/integration test script
├── README.md
```

---

# 🚀 Features

## 📊 Dashboard Analytics

* Total Inventory Count
* Issued Items
* Available Stock
* Damaged Items

## 🧾 Inventory Operations

* Add new inventory items
* Edit existing records
* Delete inventory entries
* Real-time search across all fields

## 📦 Asset Tracking Fields

* Brand & Model
* Serial Number
* Category
* Quantity
* Warranty Status
* Inventory Status
* Handover / Assignment details
* Issue & Return dates
* Notes & additional status fields

## 📤 Export & Reporting

* Export to **PDF (ReportLab)**
* Export to **Excel (.xlsx via OpenPyXL)**

## 🔎 Search & Filtering

* Global search across all inventory columns
* Instant filtering of results

## ⚙️ Reliability Features

* Database exception handling
* Safe fallback DataFrames
* UI-safe error notifications
* Schema-consistent responses

---

# 🧰 Tech Stack

| Layer           | Technology         |
| --------------- | ------------------ |
| Frontend        | Streamlit          |
| Backend         | Python             |
| Database        | PostgreSQL / MySQL |
| Data Processing | Pandas             |
| PDF Generation  | ReportLab          |
| Excel Export    | OpenPyXL           |

---

# 🗄️ Database Configuration

Create a `.env` file:

```env
DB_HOST=localhost
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

Example `db_connection.py`:

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-org/INVENTORY_MGT.git
cd INVENTORY_MGT
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Run Application

```bash
streamlit run inventory.py
```

Open:

```
http://localhost:8501
```

---

# 📈 Application Modules

## 🏠 Main Dashboard (`inventory.py`)

* Displays inventory summary metrics
* Table view of all inventory items
* Add / Edit / Delete operations
* Export functionality (PDF + Excel)
* Search + filter system

---

## 📄 Pages Folder (`pages/`)

Used for Streamlit multipage architecture:

* Additional dashboards
* Reports page
* Analytics expansion

---

## 🧪 Testing (`tests/`, `test.py`, `Inventory-test.py`)

* Unit tests for database functions
* Feature validation scripts
* Experimental UI testing

---

# 📤 Export Features

## 📄 PDF Report

* Landscape A4 format
* Structured table layout
* Timestamp included
* Professional report styling

## 📊 Excel Report

* Auto-sized columns
* Clean headers
* Structured dataset export

---

# 📌 Core Metrics Logic

```python
Total = len(df)

Issued = len(df[df["status"].str.lower() == "issued"])

Available = len(df[df["status"].str.lower().isin(
    ["in-inventory", "inventory"]
)])

Damaged = len(df[df["status"].str.lower() == "damaged"])
```

---

# ⚠️ Error Handling

* Database connection failure protection
* UI-friendly error messages
* Prevents dashboard crash on downtime
* Returns schema-safe empty DataFrame

---

# 🔐 Security Practices

* Environment variable-based configuration
* Parameterized SQL queries
* Separation of UI & database layer
* Safe input handling via Streamlit widgets

---

# 🚀 Future Enhancements

* JWT Authentication
* Role-Based Access Control (Admin/User)
* Barcode / QR Scanner Integration
* Inventory History Logs
* API Layer (FastAPI integration)
* Cloud deployment (AWS / Azure)
* Email notifications for asset assignment

---

# 🖼️ Screenshots (Recommended)

Add images for:

* Dashboard Overview
* Add Inventory Modal
* Edit Inventory Dialog
* Export Reports
* Search Functionality

---

# 👨‍💻 Author

**INVENTORY_MGT System**
Built using Streamlit + Python for efficient inventory tracking and reporting.

---

## 📄 Status

This project is currently under development. Feel free to go through it.

---

