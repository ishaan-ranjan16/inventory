from db_connection import get_connection


conn = get_connection()
cur= conn.cursor()
if conn :
    print("DB connected successfully")

cur.execute("SELECT * from inventory ")

rows = cur.fetchall()
print(type(rows))
print(rows)

cur.close()
conn.close()