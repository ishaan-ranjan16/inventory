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



# database schema -

# CREATE TABLE inventory (
#     id SERIAL PRIMARY KEY,
#     brand VARCHAR(50),
#     model VARCHAR(100),
#     serial_no VARCHAR(100) UNIQUE NOT NULL,
#     item_category VARCHAR(50),
#     warranty_status VARCHAR(50),
#     quantity INT DEFAULT 1,
#     status VARCHAR(30) NOT NULL CHECK (status IN ('In-Inventory', 'Issued', 'Damaged')),
#     hand_over_to VARCHAR(50),  -- maps to employees.employee_id
#     issue_date DATE,
#     received_from VARCHAR(100),
#     return_date DATE,
#     note TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );


# select * from inventory



# -- CREATE TABLE inventory (
# --     id SERIAL PRIMARY KEY,
# --     brand VARCHAR(50),
# --     model VARCHAR(100),
# --     serial_no VARCHAR(100) UNIQUE NOT NULL,
# --     item_category VARCHAR(50),
# --     warranty_status VARCHAR(50),
# --     quantity INT DEFAULT 1,
# --     -- status VARCHAR(30),                -- In-Inventory / Issued / Damaged
# -- 	status VARCHAR(30) NOT NULL
# -- 	CHECK (
# -- 	status IN (
# -- 	'In-Inventory',
# -- 	'Issued',
# -- 	'Damaged'
# -- 	)
# -- 	),
# --     hand_over_to VARCHAR(50),  -- stores employee_id
# --     issue_date DATE,
# --     received_from VARCHAR(100),
# --     return_date DATE,
# --     note TEXT,
# --     status_2 VARCHAR(50),
# --     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# --     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

# --     -- FOREIGN KEY (hand_over_to)
# --     --     REFERENCES employees(employee_id)
# --     --     ON DELETE SET NULL
# -- );

# -- 


# -- CREATE TABLE employees (
# --     id SERIAL PRIMARY KEY,
# --     employee_id VARCHAR(50) UNIQUE NOT NULL,
# --     employee_name VARCHAR(100) NOT NULL,
# --     designation VARCHAR(100),
# --     department VARCHAR(100),
# --     email VARCHAR(150),
# --     contact VARCHAR(20),
# --     status VARCHAR(20) NOT NULL DEFAULT 'Active'
# --         CHECK (status IN ('Active', 'Inactive')),
		
# --     created_by VARCHAR(50) DEFAULT 'system',
# --     updated_by VARCHAR(50) DEFAULT 'system',

# --     created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
# --     updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
# -- );

# -- select * from employees


# SELECT column_name
# FROM information_schema.columns
# WHERE table_name = 'inventory';

# -- SELECT column_name
# -- FROM information_schema.columns
# -- WHERE table_name = 'employees';