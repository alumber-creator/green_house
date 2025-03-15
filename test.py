from tools.database import create_connection

conn = create_connection()
cursor = conn.cursor()
cursor.execute("""
UPDATE users
SET is_admin = 1
WHERE user_id = 6130522553;
""")
conn.commit()
conn.close
