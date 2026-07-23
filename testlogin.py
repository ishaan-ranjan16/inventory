from db_connection import get_connection

def update_admin_email(new_email):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users 
            SET email = ? 
            WHERE username = 'admin' OR role = 'ADMIN'
        """, (new_email,))
        
        if cur.rowcount > 0:
            print(f"Successfully updated admin email to: {new_email}")
        else:
            print("No admin user found to update.")

# Run this once with your actual email address
update_admin_email("example123@gmail.com")