# Healthcare NL2SQL - AI-Powered Database Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.104+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vanna-2.0-purple.svg" alt="Vanna">
  <img src="https://img.shields.io/badge/License-MIT-orange.svg" alt="License">
</p>

> 🔄 Convert natural language queries into SQL instantly. No SQL knowledge required.

---

##  Demo

Ask questions in plain English and get instant SQL results with visualizations:

```
📝 "How many patients do we have?"
→ Returns: 200 patients

📝 "Show revenue by doctor"  
→ Returns: Bar chart with revenue per doctor

📝 "List all appointments from Delhi"
→ Returns: Filtered data table
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Natural Language to SQL** | Ask questions in English, get SQL queries |
| **Memory-First Architecture** | Instant responses for common queries (< 50ms) |
| **Auto-Generated Charts** | Plotly visualizations for data analysis |
| **SQL Safety** | Validates queries to prevent injection attacks |
| **Query History** | Track and re-run past queries |
| **CSV Export** | Download results for reports |
| **Dark Mode** | Eye-friendly dark theme |

---

## 🏗️ Architecture

```
User Question (Natural Language)
         │
         ▼
┌─────────────────────────────┐
│     Vanna 2.0 AI Agent      │
│  ┌───────────────────────┐   │
│  │  Agent Memory        │   │
│  │  (17 seeded queries) │   │
│  └───────────────────────┘   │
│            │                 │
│            ▼                 │
│  ┌───────────────────────┐   │
│  │   GPT-4o-mini        │   │
│  │   (LLM for new)      │   │
│  └───────────────────────┘   │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│    SQL Validation          │
│  • SELECT only             │
│  • Blocks DROP/DELETE      │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│    SQLite Database          │
│  • 1,365+ records          │
│  • 5 related tables        │
└─────────────────────────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
┌────────┐      ┌────────┐
│ Table  │      │ Chart  │
└────────┘      └────────┘
```

---

## 🛠️ Tech Stack

- **AI Framework**: [Vanna 2.0](https://vanna.ai/) - AI Agent for NL2SQL
- **LLM**: OpenAI GPT-4o-mini
- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite
- **Frontend**: Vanilla HTML/CSS/JS
- **Charts**: Plotly.js
- **Icons**: Font Awesome

---

## 📊 Database Schema

| Table | Records | Description |
|-------|---------|-------------|
| `patients` | 200 | Patient information |
| `doctors` | 15 | Doctor details |
| `appointments` | 500 | Appointment bookings |
| `treatments` | 350 | Treatment procedures |
| `invoices` | 300 | Billing information |

---

## 🚦 Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API Key

### 1. Clone & Install

```bash
git clone https://github.com/Ramakan-eng/healthcare-nl2sql.git
cd healthcare-nl2sql
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

Get your API key from: [OpenAI Platform](https://platform.openai.com/api-keys)

### 3. Start the Server

```bash
python main.py
```

### 4. Open the UI

```
Frontend: http://localhost:8080
API:      http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## 📱 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send question, get SQL results |
| `/health` | GET | Check API health |

### Example Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "how many patients do we have"}'
```

### Example Response

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

## 🎯 Example Queries

Try these questions in the UI:

| Question | SQL Generated |
|----------|---------------|
| How many patients do we have? | SELECT COUNT(*) FROM patients |
| Show all patients from Delhi | SELECT * FROM patients WHERE city = 'Delhi' |
| What is the total revenue? | SELECT SUM(total_amount) FROM invoices |
| Show revenue by doctor | JOIN query with GROUP BY |
| Show monthly appointment trend | Time-series aggregation |

---

## 📂 Project Structure

```
healthcare-nl2sql/
├── main.py              # FastAPI application
├── vanna_setup.py       # Vanna agent configuration
├── setup_database.py   # Database setup script
├── seed_memory.py       # Memory seeding script
├── clinic.db           # SQLite database
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── frontend/
│   ├── index.html     # Main UI
│   ├── styles.css     # Styling
│   └── app.js         # Frontend logic
└── README.md          # This file
```

---

## 🔒 Security Features

- ✅ SELECT-only queries (no INSERT/UPDATE/DELETE)
- ✅ Blocks dangerous SQL keywords
- ✅ Prevents system table access
- ✅ Request validation with Pydantic
- ✅ Async execution (non-blocking)

---

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

### Deploy to Render/Replit

1. Push code to GitHub
2. Connect to Render/Replit
3. Add `OPENAI_API_KEY` environment variable
4. Deploy!

---

## 📝 License

MIT License - feel free to use for learning or commercial projects.

---

## 🙏 Acknowledgments

- [Vanna AI](https://vanna.ai/) - For the amazing NL2SQL framework
- [FastAPI](https://fastapi.tiangolo.com/) - For the web framework
- [Plotly](https://plotly.com/) - For interactive charts

---

## 🤝 Connect With Me

<div align="left">
  <a href="https://linkedin.com/in/ramakant-sahu-3608002ab">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
  <a href="https://github.com/Ramakan-eng">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</div>

---

**⭐ Star the repo if you found it useful!**

Built with by Ramakant Sahu