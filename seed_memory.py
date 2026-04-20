import asyncio
from vanna_setup import agent, agent_memory
from vanna.core.user import RequestContext



ALL_QUERIES = [


# PATIENT QUERIES

{
    "question": "How many patients do we have?",
    "sql": "SELECT COUNT(*) AS total_patients FROM patients"
},
{
    "question": "List all patients from Delhi",
    "sql": "SELECT * FROM patients WHERE city = 'Delhi'"
},
{
    "question": "List all male patients",
    "sql": "SELECT * FROM patients WHERE gender = 'M'"
},
{
    "question": "Which city has the most patients?",
    "sql": """
    SELECT city, COUNT(*) AS patient_count
    FROM patients
    GROUP BY city
    ORDER BY patient_count DESC
    LIMIT 1
    """
}
,


# DOCTOR QUERIES

{
    "question": "How many doctors are there?",
    "sql": "SELECT COUNT(*) AS total_doctors FROM doctors"
},
{
    "question": "Which doctor has the most appointments?",
    "sql": """
    SELECT d.name, COUNT(a.id) AS total_appointments
    FROM doctors d
    JOIN appointments a ON d.id = a.doctor_id
    GROUP BY d.name
    ORDER BY total_appointments DESC
    LIMIT 1
    """
},
{
    "question": "Show appointments per doctor",
    "sql": """
    SELECT d.name, COUNT(a.id) AS total_appointments
    FROM doctors d
    JOIN appointments a ON d.id = a.doctor_id
    GROUP BY d.name
    ORDER BY total_appointments DESC
    """
},


# APPOINTMENT QUERIES

{
    "question": "Show all completed appointments",
    "sql": "SELECT * FROM appointments WHERE status = 'Completed'"
},
{
    "question": "Show cancelled appointments",
    "sql": "SELECT * FROM appointments WHERE status = 'Cancelled'"
},
{
    "question": "Show appointments for January 2026",
    "sql": """
    SELECT *
    FROM appointments
    WHERE strftime('%Y-%m', appointment_date) = '2026-01'
    """
},
{
    "question": "Show appointments by doctor",
    "sql": """
    SELECT d.name, a.appointment_date, a.status
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.id
    ORDER BY a.appointment_date DESC
    """
},


# FINANCIAL QUERIES

{
    "question": "What is the total revenue?",
    "sql": "SELECT SUM(total_amount) AS total_revenue FROM invoices"
},
{
    "question": "Show unpaid invoices",
    "sql": "SELECT * FROM invoices WHERE status != 'Paid'"
},
{
    "question": "What is the average invoice amount?",
    "sql": "SELECT AVG(total_amount) AS avg_invoice FROM invoices"
},
{
    "question": "Show revenue by doctor",
    "sql": """
    SELECT d.name, SUM(i.total_amount) AS total_revenue
    FROM invoices i
    JOIN appointments a ON a.patient_id = i.patient_id
    JOIN doctors d ON d.id = a.doctor_id
    GROUP BY d.name
    ORDER BY total_revenue DESC
    """
},


# TIME-BASED QUERIES

{
    "question": "Show appointments in the last 3 months",
    "sql": """
    SELECT *
    FROM appointments
    WHERE appointment_date >= date('now','-3 months')
    """
},
{
    "question": "Show monthly appointment trend",
    "sql": """
    SELECT strftime('%Y-%m', appointment_date) AS month,
           COUNT(*) AS total_appointments
    FROM appointments
    GROUP BY month
    ORDER BY month
    """
}

]
async def seed_memory():
    for qa in ALL_QUERIES:
        print(f"Training: {qa['question']}")

       
        await agent_memory.save_tool_usage(
            question=qa["question"],
            tool_name="RunSqlTool",
            args={"sql": qa["sql"]},
            success=True,
            context=None
        )

    print("\nTotal tool memories:", len(agent_memory._memories))

if __name__ == "__main__":
    asyncio.run(seed_memory())







