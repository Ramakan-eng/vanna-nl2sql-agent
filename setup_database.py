import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

conn = sqlite3.connect("clinic.db")
cursor = conn.cursor()

# Patient Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    date_of_birth DATE,
    gender TEXT,
    city TEXT,
    registered_date DATE
)
""")

# Doctor Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT,
    department TEXT,
    phone TEXT
)
""")

# Appointments Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    appointment_date DATETIME,
    status TEXT,
    notes TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(id)
)
""")

# Treatments Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS treatments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER,
    treatment_name TEXT,
    cost REAL,
    duration_minutes INTEGER,
    FOREIGN KEY(appointment_id) REFERENCES appointments(id)
)
""")

# Invoices Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    invoice_date DATE,
    total_amount REAL,
    paid_amount REAL,
    status TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
""")

# Data for generation
specializations = ["Dermatology", "Cardiology", "Orthopedics", "General", "Pediatrics"]
cities = ["Delhi","Gurugram","Noida","Faridabad","Ghaziabad","Meerut","Agra","Lucknow","Kanpur","Varanasi"]
genders = ["Male", "Female"]
appointment_statuses = ["Scheduled", "Completed", "Cancelled", "No-Show"]
invoice_statuses = ["Paid", "Pending", "Overdue"]
treatment_names = ["Consultation", "X-Ray", "Blood Test", "MRI Scan", "Physical Therapy", "Vaccination", "Surgery", "Follow-up", "Lab Work", "Ultrasound"]

# Data insertion in doctors table
doctor_ids = []
for specialization in specializations:
    for _ in range(3):
        name = fake.name()
        department = specialization
        phone = fake.phone_number() if random.random() > 0.2 else None

        cursor.execute("""
        INSERT INTO doctors (name, specialization, department, phone)
        VALUES (?, ?, ?, ?)
        """, (name, specialization, department, phone))
        doctor_ids.append(cursor.lastrowid)

# Data insertion in patients table
patient_ids = []
for _ in range(200):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email() if random.random() > 0.15 else None
    phone = fake.phone_number() if random.random() > 0.15 else None
    date_of_birth = fake.date_of_birth(minimum_age=1, maximum_age=90).isoformat()
    gender = random.choice(genders)
    city = random.choice(cities)
    registered_date = fake.date_between(start_date='-2y', end_date='-1y').isoformat()

    cursor.execute("""
    INSERT INTO patients (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date))
    patient_ids.append(cursor.lastrowid)



# Data insertion in appointments table
doctor_weights = [random.randint(1, 10) for _ in range(15)]
weighted_doctor_ids = []
for doc_id, weight in zip(doctor_ids, doctor_weights):
    weighted_doctor_ids.extend([doc_id] * weight)

# Create   patients
patient_weights = [random.randint(1, 20) for _ in range(200)]
weighted_patient_ids = []
for pat_id, weight in zip(patient_ids, patient_weights):
    weighted_patient_ids.extend([pat_id] * weight)

appointment_ids = []
base_date = datetime.now()
start_date = base_date - timedelta(days=365)

for _ in range(500):
    patient_id = random.choice(weighted_patient_ids)
    doctor_id = random.choice(weighted_doctor_ids)
    appointment_date = fake.date_time_between(start_date=start_date, end_date=base_date).strftime('%Y-%m-%d %H:%M:%S')
    status = random.choice(appointment_statuses)
    notes = fake.sentence(nb_words=10) if random.random() > 0.2 else None

    cursor.execute("""
    INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
    VALUES (?, ?, ?, ?, ?)
    """, (patient_id, doctor_id, appointment_date, status, notes))
    appointment_ids.append(cursor.lastrowid)

# Insert 350 treatments 
completed_appointment_ids = []
for appt_id in appointment_ids:
    cursor.execute("SELECT status FROM appointments WHERE id = ?", (appt_id,))
    status = cursor.fetchone()[0]
    if status == "Completed":
        completed_appointment_ids.append(appt_id)

treatment_ids = []
for _ in range(350):
    appointment_id = random.choice(completed_appointment_ids)
    treatment_name = random.choice(treatment_names)
    cost = round(random.uniform(50, 5000), 2)
    duration_minutes = random.choice([15, 30, 45, 60, 90, 120])

    cursor.execute("""
    INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes)
    VALUES (?, ?, ?, ?)
    """, (appointment_id, treatment_name, cost, duration_minutes))
    treatment_ids.append(cursor.lastrowid)

# Insert 300 invoices
invoice_patient_ids = random.choices(patient_ids, k=300)
for patient_id in invoice_patient_ids:
    invoice_date = fake.date_between(start_date='-1y', end_date='today').isoformat()
    total_amount = round(random.uniform(50, 5000), 2)
    status = random.choice(invoice_statuses)

    if status == "Paid":
        paid_amount = total_amount
    elif status == "Pending":
        paid_amount = 0
    else:  
        paid_amount = round(random.uniform(0, total_amount * 0.5), 2)

    cursor.execute("""
    INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status)
    VALUES (?, ?, ?, ?, ?)
    """, (patient_id, invoice_date, total_amount, paid_amount, status))

conn.commit()

# counts
cursor.execute("SELECT COUNT(*) FROM patients")
patient_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM doctors")
doctor_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM appointments")
appointment_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM treatments")
treatment_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM invoices")
invoice_count = cursor.fetchone()[0]

conn.close()

print(f"Created {patient_count} patients, {doctor_count} doctors, {appointment_count} appointments, {treatment_count} treatments, {invoice_count} invoices")
