# Healthcare NL2SQL API

A FastAPI application that converts natural language questions into SQL queries using Vanna 2.0 AI agnet and then run this by using inbult register tool and get output.



## Features

- **Natural Language to SQL**: Ask questions in plain English, get SQL queries and results
- **Memory-First Architecture**: Searches seeded Q&A pairs first for instant responses
- **AI-Powered SQL Generation**: Falls back to OpenAI GPT-4 mini for new questions
- **Interactive Charts**: Automatically generates Plotly visualizations for result sets
- **SQLite Database**: Simulates a clinic management system with realistic dummy data
- **Async Performance**: Non-blocking API using FastAPI and async/await
- **SQL Safety**: Validates queries to prevent injection attacks and dangerous operations

## Project Architecture

```
Vanna 2.0 Agent (AI backbone)
    ↓
UserResolver (identifies user)
    ↓
DemoAgentMemory (stores Q&A pairs)
    ↓
ToolRegistry (RunSqlTool, VisualizeDataTool, SaveQuestionToolArgsTool)
    ↓
OpenAI LLM Service (GPT-4 mini for SQL generation)
    ↓
SqliteRunner (executes SQL against clinic.db)
    ↓
FastAPI Application (HTTP endpoints: /chat, /health)
```

**Request Flow**:
1. User sends natural language question → POST `/chat`
. LLM generates new SQL → validates → executes → returns result
5. Response includes: message, SQL query, columns, rows, row_count, chart (if applicable)

## Database Schema

### tables (5 total):

- **patients**: 200 records - Patient information (name, email, phone, city, DOB, gender, registration date)
- **doctors**: 15 records - Doctor details (name, specialization, department, phone)
- **appointments**: 500 records - Appointment booking (patient_id, doctor_id, date, status, notes)
- **treatments**: 350 records - Treatment procedures (appointment_id, name, cost, duration)
- **invoices**: 300 records - Billing (patient_id, date, total_amount, paid_amount, status)

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip package manager
- OpenAI API key (from https://platform.openai.com)
### Step 0: Set Up Environment Variables

Create a `.env` file in the project root with your OpenAI API key:
# Edit .env with your API key
# OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```


### Step 1: Clone/Navigate to Project

```bash
cd d:\vanna-nl2sql-agent
```

### Step 2: Create Virtual Environment 


# on Windows Command Prompt
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```
pip install -r requirements.txt
```

**Key packages installed**:
- `vanna>=2.0.0` - AI agent for NL2SQL
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `plotly` - Chart generation
- `pandas` - Data manipulation
- `python-dotenv` - Environment variables
- 'Faker' - For data generation

### Step 4: Set Up Database

Create the SQLite database and populate it with dummy data:

```bash
python setup_database.py
```

**Output:**
```
Created 200 patients, 15 doctors, 500 appointments, 350 treatments, 300 invoices
```

This creates `clinic.db` in the project root.

### Step 5: Seed Agent Memory

Pre-populate the agent's memory with 17 example Q&A pairs so it has a head start:

```bash
python seed_memory.py
```

**Output:**
```
vanna setup successfully
Training: How many patients do we have?
Training: List all patients from Delhi
Training: List all male patients
Training: Which city has the most patients?
...
Total tool memories: 17
```

This teaches the agent common healthcare queries and their SQL equivalents.

### Step 6: Start the API Server

```bash
python main.py
```
"or"

uvicorn main:app --port 8000

**Expected Output:**
```
vanna setup successfully
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

The server is now running and ready to accept requests!

## API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### 1. POST `/chat` - Convert Natural Language to SQL

**Purpose**: Accept a natural language question and return SQL query, results, and optional visualization.

**Request**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "how many patients we have"}'
```

**Request Body**:
```json
{
  "question": "how many patients we have"
}
```

**Response** (200 OK):
```json
{
  "message": "Here is 1 result.",
  "sql_query": "SELECT COUNT(*) AS total_patients FROM patients",
  "columns": ["total_patients"],
  "rows": [[200]],
  "row_count": 1,
  "chart": null,
  "chart_type": null
}
```

---

#### 2. More Example Requests

**Example 2**: List patients from a specific city

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me all patients from Delhi"}'
```

**Response**:
```json
{
  "message": "Here are 42 results.",
  "sql_query": "SELECT * FROM patients WHERE city = 'Delhi'",
  "columns": ["id", "first_name", "last_name", "email", "phone", "date_of_birth", "gender", "city", "registered_date"],
  "rows": [
    [1, "John", "Smith", "john@example.com", "9876543210", "1985-05-15", "M", "Delhi", "2024-01-10"],
    [2, "Jane", "Doe", "jane@example.com", "9876543211", "1990-03-20", "F", "Delhi", "2024-02-15"],
    ...
  ],
  "row_count": 42,
  "chart": null,
  "chart_type": null
}
```

**Example 3**: Show revenue by doctor (with chart)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Show revenue by doctor"}'
```

**Response** (includes chart):
```json
{
  "message": "Here are 45 results.",
  "sql_query": "SELECT d.name, SUM(i.total_amount) AS total_revenue FROM invoices i JOIN appointments a ON a.id = i.appointment_id JOIN doctors d ON d.id = a.doctor_id GROUP BY d.name ORDER BY total_revenue DESC",
  "columns": ["name", "total_revenue"],
  "rows": [
    ["Dr. Smith", 45250.50],
    ["Dr. Johnson", 38900.25],
    ...
  ],
  "row_count": 45,
  "chart": {
    "data": [...],
    "layout": {...}
  },
  "chart_type": "bar"
}
```

---

#### 3. GET `/health` - System Health Check

**Purpose**: Monitor the health of the API server, database connection, and memory status.

**Request**:
```bash
curl http://localhost:8000/health
```

**Response** (200 OK):
```json
{
  "status": "ok",
  "database": "connected",
  "agent_memory_items": 17
}
```

**Response Explanation**:
- `status`: "ok" = server is running
- `database`: "connected" or error details if connection fails
- `agent_memory_items`: Number of Q&A pairs stored in memory (should be ≥ 17 after seeding)

---

## Response Schema

All `/chat` responses follow this structure:

```json
{
  "message": "string - Human-readable summary",
  "sql_query": "string or null - The executed SQL query",
  "columns": ["array of column names or null"],
  "rows": ["array of result rows or null"],
  "row_count": "number or null - Total results returned",
  "chart": "object or null - Plotly graph JSON",
  "chart_type": "string or null - 'bar', 'line', or 'pie'"
}
```

## Common Use Cases

### 1. Count Records
```
Q: "How many patients do we have?"
A: SELECT COUNT(*) AS total_patients FROM patients
```

### 2. Aggregations
```
Q: "What is the total revenue?"
A: SELECT SUM(total_amount) AS total_revenue FROM invoices
```

### 3. Time-Based Queries
```
Q: "Show appointments in the last 3 months"
A: SELECT * FROM appointments WHERE appointment_date >= date('now', '-3 months')
```

### 4. Joins
```
Q: "Show revenue by doctor"
A: SELECT d.name, SUM(i.total_amount) FROM invoices i 
   JOIN appointments a ON a.id = i.appointment_id 
   JOIN doctors d ON d.id = a.doctor_id GROUP BY d.name
```

## Error Handling

### 1. Invalid SQL (400 Bad Request)
```json
{
  "detail": "SQL validation failed: INSERT not allowed"
}
```
*Only SELECT queries are permitted for security.*

### 2. No SQL Generated (200 OK)
```json
{
  "message": "Could not generate SQL",
  "sql_query": null,
  "columns": null,
  "rows": null,
  "row_count": null,
  "chart": null,
  "chart_type": null
}
```
*Try rephrasing your question or ensure it matches the database schema.*

### 3. Database Connection Error (500 Server Error)
```json
{
  "detail": "Execution error: database connection failed"
}
```
*Check that clinic.db exists and is accessible.*

## Configuration

### Environment Variables (`.env` file)

The application automatically loads configuration from a `.env` file in the project root using `python-dotenv`.

**Example `.env` file**:
```env
# Required: Your OpenAI API Key
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE

# Optional
DATABASE_PATH=./clinic.db
VANNA_MODEL=gpt-4o-mini
```

###  View Uvicorn Docs

Visit: `http://localhost:8000/docs` for interactive Swagger API documentation

## Security Considerations

✅ **Implemented**:
- SQL validation (no INSERT, UPDATE, DELETE, DROP)
- No access to system tables (SQLITE_MASTER)
- Async query execution (non-blocking)
- Request validation (Pydantic models)



## Troubleshooting

### Issue: "Could not generate SQL"

**Cause**: Question doesn't match any memory entries AND LLM failed to generate SQL

**Solution**:
1. Try a simpler question
2. Check that the database tables exist: `python setup_database.py`
3. Verify OpenAI API key is valid
4. Check server logs for error details

### Issue: "Execution error: SqliteRunner.run_sql() missing 1 required positional argument"

**Cause**: Incorrect arguments passed to SQL runner

**Solution**: Ensure `RunSqlToolArgs` wrapper is used in `main.py`:
```python
args = RunSqlToolArgs(sql=sql_query)
result = await sql_runner.run_sql(args, context)
```

### Issue: Server won't start

**Cause**: Port 8000 already in use OR missing dependencies

**Solution**:
```bash
# Check if port is in use
netstat -ano | findstr :8000

# Kill process using port (Windows)
taskkill /PID <PID> /F

# OR use different port in main.py
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
```


## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Create database: `python setup_database.py`
3. Seed memory: `python seed_memory.py`
4. Start server: `python main.py`
5. Test API: `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"question": "how many patients we have"}'`

