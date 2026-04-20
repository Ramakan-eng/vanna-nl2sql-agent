import sqlite3


conn = sqlite3.connect("clinic.db")
cursor = conn.cursor()

cursor.execute("""
  SELECT strftime('%Y-%m', appointment_date) AS month,
           COUNT(*) AS total_appointments
    FROM appointments
    GROUP BY month
    ORDER BY month
""")
result= cursor.fetchall()
print(result)