# 📦 Inventory Management System (INVENTORY_MGT)

A modern, production-style **Inventory Management System** built using **Streamlit**, **Pandas**, and a relational database.  
It provides a clean dashboard for managing inventory assets, tracking item lifecycle, and generating exportable reports in **PDF** and **Excel** formats.

---

# 🚀 Features

## 📊 Dashboard Analytics
- Total Inventory Count
- Issued Items
- Available Stock
- Damaged Items

## 🧾 Inventory Operations
- Add new inventory items
- Edit existing records
- Delete inventory entries
- Real-time global search across all fields

## 📦 Asset Tracking Fields
- Brand & Model
- Serial Number
- Category
- Quantity
- Warranty Status
- Inventory Status
- Handover / Assignment details
- Issue & Return dates
- Notes & status tracking

## 📤 Export & Reporting
- Export inventory report as **PDF (ReportLab)**
- Export inventory report as **Excel (.xlsx via OpenPyXL)**

## ⚙️ Reliability Features
- Database exception handling
- Safe fallback DataFrames
- UI-safe error notifications
- Schema-consistent responses

---

# 🧰 Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | Streamlit |
| Backend | Python |
| Database | PostgreSQL / MySQL |
| Data Processing | Pandas |
| PDF Generation | ReportLab |
| Excel Export | OpenPyXL |
| Testing | Pytest |

---

# 📁 Project Structure

INVENTORY_MGT/
│
├── pages/                      # Streamlit multipage app (optional future expansion)
├── tests/                      # Pytest-based test cases
│   ├── test_db_connection.py
│   ├── test_inventory_operations.py
│   └── test_ui_logic.py
│
├── __pycache__/               # Python cache (auto-generated)
├── .pytest_cache/             # Pytest cache (auto-generated)
│
├── db_connection.py           # Database connection handler (PostgreSQL/MySQL)
├── inventory.py               # Main Streamlit dashboard application
├── Inventory-test.py          # Experimental / UI testing script
├── test.py                    # Legacy test script (can be migrated to pytest)
│
├── .env                       # Environment variables (DB credentials, secrets)
├── .gitignore                # Git ignore rules
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
│
└── exports/                  # (Optional) Generated PDF/Excel reports storage

---

# 🗄️ Database Configuration

Create a `.env` file:

```env
DB_HOST=localhost
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/your-org/INVENTORY_MGT.git
cd INVENTORY_MGT
2️⃣ Create Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
macOS / Linux
python3 -m venv venv
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run Application
streamlit run inventory.py

Open in browser:

http://localhost:8501
🧪 Testing (pytest)

This project uses pytest for automated testing.

📌 Install pytest
pip install pytest

Or:

pip install -r requirements.txt
▶️ Run Tests
pytest

Verbose mode:

pytest -v
📁 Test Structure
tests/
├── test_db_connection.py
├── test_inventory_operations.py
├── test_ui_logic.py
🧾 Example Test Case
from db_connection import get_connection

def test_db_connection():
    conn = get_connection()
    assert conn is not None
    conn.close()
⚙️ What is tested
Database connection
Insert / update / delete operations
Data validation
Schema integrity
Edge cases handling
📈 Application Modules
🏠 Main Dashboard (inventory.py)
Inventory overview metrics
Add / edit / delete items
Search & filtering
Export PDF & Excel
📄 Pages Folder (pages/)
Extra dashboards
Analytics expansion
Future modules
🧪 Testing Module

Ensures stability using pytest-based testing

📤 Export Features
📄 PDF Report
A4 Landscape format
Styled table layout
Timestamp included
📊 Excel Report
Auto-sized columns
Clean headers
Structured export
🔐 Security Practices
Environment variables (.env)
Parameterized queries
Safe input handling
Separation of UI and DB logic
🚀 Future Enhancements
JWT Authentication
Role-based access control
Barcode / QR scanning
Inventory history logs
FastAPI backend integration
Cloud deployment (AWS / Azure)
Email notifications
👨‍💻 Author

Inventory Management System
Built using Streamlit + Python

📌 Status

Project under active development.