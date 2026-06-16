import streamlit as st

st.set_page_config(
    page_title="Home-Page",
    layout="wide"
)

st.title("🏠 Home..")

st.markdown("---")

# Welcome - section
st.subheader("👋 Welcome.")

st.write("""
Welcome to the Inventory Management System.

Use the sidebar navigation to access:
- 📦 Inventory Section
- 👨‍💼 Employee Section
- 📊 Reports & Analytics, etc..
""")

# Dashboard Cards
st.subheader("📌 Quick Access -")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📦 Manage Inventory")

with col2:
    st.success("👨‍💼 Manage Employees")

with col3:
    st.warning("📊 View Reports")

st.markdown("---")

# System-
st.subheader("📝 System Overview")

st.write("""
This dashboard helps you manage:

✅ Inventory Records

✅ Employee Details
         
✅ Search & Filters
         
✅ Status Tracking
         
✅ Dashboard Reporting
""")
st.markdown("---")

# Footer
st.caption("Inventory Management System • Dashboard")
#Footer
st.caption(
    """
    <div style='text-align:left; color:black;'>
        © 2026 Inventory Management System • Dashboard
    </div>
    """,
    unsafe_allow_html=True
)
# -----------------------
# st.markdown(
#     """
#     <div style='text-align:center; color:gray;'>
#         © 2026 Inventory Management System <br>
#         Built with ❤️ using Streamlit
#     </div>
#     """,
#     unsafe_allow_html=True
# )



# import streamlit as st

# # -----------------------
# # Page Configuration
# # -----------------------
# st.set_page_config(
#     page_title="Inventory Management System",
#     page_icon="📦",
#     layout="wide"
# )

# # -----------------------
# # Header
# # -----------------------
# st.title("📦 Inventory Management System")
# st.caption("Manage inventory, employees, and business operations from one dashboard.")

# st.markdown("---")

# # -----------------------
# # Welcome Banner
# # -----------------------
# st.container()

# st.markdown("""
# ### 👋 Welcome Back

# This system helps you efficiently manage inventory records, employee details,
# reports, and business operations in a centralized dashboard.
# """)

# # -----------------------
# # Dashboard Metrics
# # -----------------------
# st.subheader("📊 Dashboard Overview")

# col1, col2, col3, col4 = st.columns(4)

# with col1:
#     st.metric(
#         label="📦 Total Products",
#         value="1,250",
#         delta="+25"
#     )

# with col2:
#     st.metric(
#         label="👨‍💼 Employees",
#         value="85",
#         delta="+3"
#     )

# with col3:
#     st.metric(
#         label="📋 Pending Orders",
#         value="42",
#         delta="-5"
#     )

# with col4:
#     st.metric(
#         label="💰 Revenue",
#         value="₹4.8L",
#         delta="+12%"
#     )

# st.markdown("---")

# # -----------------------
# # Quick Access
# # -----------------------
# st.subheader("⚡ Quick Access")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.info("""
#     ### 📦 Inventory

#     - Add Products
#     - Update Stock
#     - Track Inventory
#     """)

# with col2:
#     st.success("""
#     ### 👨‍💼 Employees

#     - Employee Records
#     - Attendance
#     - Department Details
#     """)

# with col3:
#     st.warning("""
#     ### 📊 Reports

#     - Sales Reports
#     - Stock Reports
#     - Analytics Dashboard
#     """)

# st.markdown("---")

# # -----------------------
# # System Features
# # -----------------------
# st.subheader("✨ System Features")

# left, right = st.columns(2)

# with left:
#     st.markdown("""
#     ✅ Inventory Management

#     ✅ Employee Management

#     ✅ Stock Monitoring

#     ✅ Search & Filters
#     """)

# with right:
#     st.markdown("""
#     ✅ Report Generation

#     ✅ Status Tracking

#     ✅ Dashboard Analytics

#     ✅ Data Management
#     """)

# st.markdown("---")

# # -----------------------
# # Notifications
# # -----------------------
# st.subheader("🔔 Recent Activity")

# st.success("Stock updated successfully for Product ID #1024")
# st.info("New employee added to Sales Department")
# st.warning("5 products are running low on stock")

# st.markdown("---")

# # -----------------------
# # Footer
# # -----------------------
# st.markdown(
#     """
#     <div style='text-align:center; color:gray;'>
#         © 2026 Inventory Management System <br>
#         Built with ❤️ using Streamlit
#     </div>
#     """,
#     unsafe_allow_html=True
# )
