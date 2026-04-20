import re
import asyncio
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

from vanna_setup import agent, agent_memory, sql_runner, RunSqlTool
from vanna.core.user import RequestContext
from vanna.capabilities.sql_runner import RunSqlToolArgs


# CHART HELPERS


PLOTLY_AVAILABLE = False
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    pass


def should_create_chart(question: str, row_count: int) -> bool:
    if row_count <= 1:
        return False
    question_lower = question.lower()
    chart_keywords = ["show", "chart", "graph", "visual", "compare", "trend",
                      "distribution", "by", "top", "per", "each"]
    return any(kw in question_lower for kw in chart_keywords)


def detect_chart_type(columns: List[str]) -> str:
    col_str = " ".join(columns).lower()
    if any(kw in col_str for kw in ["date", "month", "year", "day", "time", "trend"]):
        return "line"
    if any(kw in col_str for kw in ["percent", "percentage", "ratio", "proportion"]):
        return "pie"
    return "bar"


def create_chart(columns: List[str], rows: List[List[Any]], chart_type: str = "bar") -> Optional[Dict]:
    if not PLOTLY_AVAILABLE or not rows or not columns:
        return None
    try:
        x_values = [str(row[0]) if row[0] is not None else "None" for row in rows]
        y_values = [float(row[1]) if len(row) > 1 and row[1] is not None else 0 for row in rows]

        if chart_type == "line":
            fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode="lines+markers"))
        elif chart_type == "pie":
            fig = go.Figure(data=go.Pie(labels=x_values, values=y_values, hole=0.3))
        else:
            fig = go.Figure(data=go.Bar(x=x_values, y=y_values))

        fig.update_layout(
            xaxis_title=columns[0] if columns else "",
            yaxis_title="Value",
            font={"family": "Arial", "size": 12},
            paper_bgcolor="white",
            plot_bgcolor="#f8f9fa",
            margin=dict(t=40, l=40, r=40, b=40)
        )
        return fig.to_dict()
    except Exception:
        return None



# FASTAPI APP



app = FastAPI(title="Healthcare NL2SQL API", version="1.0.0")



# REQUEST / RESPONSE MODELS



class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class ChatResponse(BaseModel):
    message: str
    sql_query: Optional[str] = None
    columns: Optional[List[str]] = None
    rows: Optional[List[List[Any]]] = None
    row_count: Optional[int] = None
    chart: Optional[Dict] = None
    chart_type: Optional[str] = None



# SQL VALIDATION 



DANGEROUS = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "EXEC"]

def validate_sql(sql: str):
    sql_upper = sql.upper()

 
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries allowed"

    for word in DANGEROUS:
        if word in sql_upper:
            return False, f"{word} not allowed"

    if "SQLITE_MASTER" in sql_upper:
        return False, "Access to system tables not allowed"

    return True, ""
    



#  PARSE AGENT OUTPUT

def parse_agent_output(text: str):
    sql_match = re.search(r"(SELECT.*?)(?:;|$)", text, re.IGNORECASE | re.DOTALL)
    sql = sql_match.group(1).strip() if sql_match else None
    return sql


# HEALTH ENDPOINT


@app.get("/health")
def health():
    memory_count = 0
    try:
        # DemoAgentMemory 
        if hasattr(agent_memory, '_memories'):
            memory_count = len(agent_memory._memories)
        elif hasattr(agent_memory, 'get_all'):
            entries = agent_memory.get_all()
            memory_count = len(entries) if entries else 0
    except Exception:
        pass

    return {
        "status": "ok",
        "database": "connected",
        "agent_memory_items": memory_count
    }

# CHAT ENDPOINT


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    context = RequestContext(user_id="1")

    
    try:
        response_gen = agent.send_message(context, request.question)
        # print("response_generated",response_gen)
        response_text = ""
        async for chunk in response_gen:
            if hasattr(chunk, "simple_component") and chunk.simple_component:
                response_text += chunk.simple_component.text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

   
    sql_query = parse_agent_output(response_text)
    print("sql_query",sql_query)
    if not sql_query:
        return ChatResponse(message="Could not generate SQL", sql_query=None)

    
    is_valid, error = validate_sql(sql_query)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    try:
        
        args = RunSqlToolArgs(sql=sql_query)
        result = await sql_runner.run_sql(args, context)
        print(f"DEBUG: Result type: {type(result)}")
        print(f"DEBUG: Result: {result}")
        
       
        import pandas as pd
        if isinstance(result, pd.DataFrame):
            columns = list(result.columns)
            rows = [list(row) for row in result.itertuples(index=False, name=None)]
            row_count = len(rows)
        elif hasattr(result, 'columns') and hasattr(result, 'itertuples'):
            columns = list(result.columns)
            rows = [list(row) for row in result.itertuples(index=False, name=None)]
            row_count = len(rows)
        else:
            
            if hasattr(result, 'df'):
                df = result.df
                if isinstance(df, pd.DataFrame):
                    columns = list(df.columns)
                    rows = [list(row) for row in df.itertuples(index=False, name=None)]
                    row_count = len(rows)
                else:
                    columns = []
                    rows = []
                    row_count = 0
            else:
                columns = []
                rows = []
                row_count = 0
    except Exception as e:
        print(f"DEBUG: Exception in SQL execution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

    
    chart = None
    chart_type = None
    if should_create_chart(request.question, row_count):
        chart_type = detect_chart_type(columns)
        chart = create_chart(columns, rows, chart_type)

    
    if row_count == 0:
        message = "No data found for your question."
    elif row_count == 1:
        message = "Here is 1 result."
    else:
        message = f"Here are {row_count} results."
    
    # mdresult = {columns[i]: rows[0][i] for i in range(len(columns))}
    # print("mdresult:",mdresult)
    return ChatResponse(
        message=message,
        sql_query=sql_query,
        columns=columns,
        rows=rows,
        row_count=row_count,
        chart=chart,
        chart_type=chart_type
    )
    


# RUN SERVER


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
