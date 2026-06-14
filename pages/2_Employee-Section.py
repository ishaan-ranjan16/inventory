import streamlit as st
import pandas as pd
from db_connection import get_connection

st.set_page_config(
    page_title="Employee-Section",
    layout="wide"
)

st.title("👨‍💼 Employee Dashboard")

# =========================
# DATABASE FUNCTIONS
# =========================

def fetch_employees():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM employees
            ORDER BY id DESC
        """)

        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]

        cur.close()
        conn.close()

        return pd.DataFrame(rows, columns=cols)

    except Exception as e:
        st.error(f"DB Error: {e}")
        return pd.DataFrame()

def insert_employee(data):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO employees (
                employee_id,
                employee_name,
                designation,
                department,
                email,
                contact,
                status,
                created_by,
                updated_by
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)

        conn.commit()

    except Exception as e:
        st.error(f"DB Error: {e}")

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def update_employee(old_emp_id, data):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE employees
            SET
                employee_id=%s,
                employee_name=%s,
                designation=%s,
                department=%s,
                email=%s,
                contact=%s,
                status=%s,
                updated_by=%s,
                updated_at=NOW()
            WHERE employee_id=%s
        """, data)

        conn.commit()

    except Exception as e:
        st.error(f"DB Error: {e}")
        raise e

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def delete_employee(emp_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM employees
            WHERE employee_id=%s
        """, (emp_id,))

        conn.commit()

    except Exception as e:
        st.error(f"DB Error: {e}")

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()



# def update_employee(emp_id, data):
#     try:
#         conn = get_connection()
#         cur = conn.cursor()

#         cur.execute("""
#             UPDATE employees
#             SET
#                 employee_id=%s,
#                 employee_name=%s,
#                 designation=%s,
#                 department=%s,
#                 email=%s,
#                 contact=%s,
#                 status=%s,
#                 updated_by=%s,
#                 updated_at=NOW()
#             WHERE employee_id=%s
#         """, data)

#         conn.commit()

#     except Exception as e:
#         st.error(f"DB Error: {e}")

#     finally:
#         if 'cur' in locals():
#             cur.close()
#         if 'conn' in locals():
#             conn.close()



# ***************************
# LOAD DATA
# =========================
df = fetch_employees()

# =========================
# METRICS
# =========================

total_emp = len(df)

active_emp = len(df[df["status"] == "Active"]) if not df.empty else 0

st.markdown("### 📊 Employee Overview")

c1, c2 = st.columns(2)
c1.metric("Total Employees", total_emp)
c2.metric("Active Employees", active_emp)

st.divider()

# =========================
# ADD EMPLOYEE
# =========================

st.subheader("📝 Add Employee")

with st.form("add_employee", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        employee_id = st.text_input("Employee ID",placeholder="Enter Emp_ID")
        employee_name = st.text_input("Employee Name",placeholder="Enter Emp_Name")
        designation = st.text_input("Designation",placeholder="Enter Emp_Designation")
        department = st.text_input("Department",placeholder="Enter Emp_Dept.")

    with col2:
        email = st.text_input("Email",placeholder="Enter email.")
        contact = st.text_input("Contact",placeholder="Enter Emp_contact")
        status = st.selectbox("Status", ["Active", "Inactive","NA"])

    submit = st.form_submit_button("➕ Add Employee")

    if submit:

        if employee_id == "" or employee_name == "":
            st.error("Employee ID and Name are required")

        else:
            insert_employee((
                employee_id,
                employee_name,
                designation,
                department,
                email,
                contact,
                status,
                "system",   # created_by
                "system"    # updated_by
            ))

            st.success("Employee added successfully")
            st.rerun()

# ====================
# EMPLOYEE LIST -
# ====================
st.divider()
st.subheader("📋 Employee List")

if df.empty:
    st.info("No employees found")

else:
    st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# EDIT / DELETE SECTION
# =========================
st.divider()
st.markdown("### 🛠 Manage Employees")

#-----------------------------------------------------------------
# Employee Search
employee_search = st.text_input(
    "🔍 Search Employee",
    placeholder="Search Filter.."
)

filtered_emp_df = df.copy()

if employee_search:
    filtered_emp_df = filtered_emp_df[
        filtered_emp_df.apply(
            lambda r: r.astype(str).str.contains(
                employee_search,
                case=False,
                na=False
            ).any(),
            axis=1
        )
    ]

st.write(f"Found {len(filtered_emp_df)} employee(s)")
#----------------------------------------------------------------------
# for i, row in df.iterrows():
for i, row in filtered_emp_df.iterrows():

    with st.expander(f"{row['employee_name']} ({row['employee_id']})"):

        with st.form(f"edit_{row['employee_id']}"):

            c1, c2 = st.columns(2)

            with c1:
                emp_id = st.text_input("Employee ID", value=row["employee_id"])
                name = st.text_input("Name", value=row["employee_name"])
                designation = st.text_input("Designation", value=row["designation"])
                department = st.text_input("Department", value=row["department"])

            with c2:
                email = st.text_input("Email", value=row["email"])
                contact = st.text_input("Contact", value=row["contact"])
                status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    index=0 if row["status"] == "Active" else 1
                )

            save = st.form_submit_button("💾 Save")
            delete = st.form_submit_button("🗑 Delete")

        if save:
            update_employee(row["employee_id"], (
                emp_id,
                name,
                designation,
                department,
                email,
                contact,
                status,
                "system",        # updated_by
                row["employee_id"]
            ))

            st.success("Employee updated")
            st.rerun()

        if delete:
            delete_employee(row["employee_id"])
            st.warning("Employee deleted")
            st.rerun()

# ======================
# SEARCH
# ======================
st.divider()
st.subheader("🔍 Search Employees")

keyword = st.text_input("Search🔍",placeholder="Search Filter..")

filtered = df.copy()

if keyword:
    filtered = filtered[
        filtered.apply(
            lambda r: r.astype(str).str.contains(keyword, case=False, na=False).any(),
            axis=1
        )
    ]

st.dataframe(filtered, use_container_width=True, hide_index=True)
st.divider()

# =========================
# EMPLOYEE → INVENTORY VIEW
# =========================

# st.subheader("💻 Employee Asset Details")

# if not df.empty and "inventory" in st.session_state:

#     employee_list = df.apply(
#         lambda x: f"{x['employee_id']} - {x['employee_name']}",
#         axis=1
#     ).tolist()

#     selected = st.selectbox("Select Employee", employee_list)

#     emp_id = selected.split(" - ")[0]

#     emp_assets = st.session_state.inventory[
#         st.session_state.inventory["handover_to"] == emp_id
#     ]

#     st.write(f"📦 Assigned Assets: {len(emp_assets)}")
#     st.dataframe(emp_assets, use_container_width=True, hide_index=True)

# else:
#     st.info("No inventory data available")

# =========================
# EMPLOYEE → INVENTORY VIEW
# =========================

# st.subheader("💻 Employee Asset Details")

# if not df.empty:

#     employee_list = df.apply(
#         lambda x: f"{x['employee_id']} - {x['employee_name']}",
#         axis=1
#     ).tolist()

#     selected = st.selectbox(
#         "Select Employee",
#         employee_list
#     )

#     emp_id = selected.split(" - ")[0]

#     # emp_assets = fetch_employee_assets(emp_id)

#     st.write(f"📦 Assigned Assets: {len(emp_assets)}")

#     if not emp_assets.empty:
#         st.dataframe(
#             emp_assets,
#             use_container_width=True,
#             hide_index=True
#         )
#     else:
#         st.info("No assets assigned")

# else:
#     st.info("No employees available")s