from werkzeug.security import generate_password_hash
from database.db_config import get_db_connection

password = generate_password_hash("admin123")

conn = get_db_connection()
cursor = conn.cursor()

sql = """
INSERT INTO staff
(full_name, username, password, role, email)
VALUES (%s,%s,%s,%s,%s)
"""

values = (
    "Hospital Administrator",
    "admin",
    password,
    "Admin",
    "admin@hospital.com"
)

cursor.execute(sql, values)

conn.commit()

print("Admin Created Successfully")

cursor.close()
conn.close()