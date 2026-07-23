import sqlite3

conn = sqlite3.connect("inventory.db")
cur = conn.cursor()

cur.execute("SELECT * FROM inventory")
print(cur.fetchall())

conn.close()
# import streamlit as st
# st.write(st.__version__)