
from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool, SaveTextMemoryTool

from vanna.integrations.openai import OpenAILlmService
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.core.system_prompt import SystemPromptBuilder
from typing import List, Dict, Any


class CustomSystemPromptBuilder(SystemPromptBuilder):

    async def build_system_prompt(
        self,
        user: User,
        tool_schemas: List[Dict[str, Any]],
        context: Dict[str, Any]=None
    ) -> str:

        schema = """
Database schema:
- patients: id (INTEGER PRIMARY KEY), first_name (TEXT), last_name (TEXT), email (TEXT), phone (TEXT), date_of_birth (DATE), gender (TEXT), city (TEXT), registered_date (DATE)
- doctors: id (INTEGER PRIMARY KEY), name (TEXT), specialization (TEXT), department (TEXT), phone (TEXT)
- appointments: id (INTEGER PRIMARY KEY), patient_id (INTEGER), doctor_id (INTEGER), appointment_date (DATETIME), status (TEXT), notes (TEXT)
- treatments: id (INTEGER PRIMARY KEY), appointment_id (INTEGER), treatment_name (TEXT), cost (REAL), duration_minutes (INTEGER)
- invoices: id (INTEGER PRIMARY KEY), patient_id (INTEGER), invoice_date (DATE), total_amount (REAL), paid_amount (REAL), status (TEXT)
"""

        prompt = f"""
{schema}

You are an AI assistant for a healthcare database. Use the tools to answer questions.

First, check memory for similar questions. If found, adapt the SQL. If not, generate new SQL using the schema, then execute it.
"""

        for tool in tool_schemas:
            prompt += f"\n- {tool['name']}: {tool['description']}"

        return prompt





#  environment variables
import os
from dotenv import load_dotenv

load_dotenv()

# Configure your LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



llm = OpenAILlmService(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)


sql_runner = SqliteRunner(database_path="./clinic.db")

#  database
db_tool = RunSqlTool(
    sql_runner=sql_runner
)

#  agent memory
agent_memory = DemoAgentMemory(max_items=1000)

#  authentication
class DefaultUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(id="1", name="ramakant")
user_resolver = DefaultUserResolver()

#  agent
tools = ToolRegistry()
tools.register_local_tool(db_tool, access_groups=['admin', 'user'])
tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin',"user"])
tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'user'])
tools.register_local_tool(SaveTextMemoryTool(), access_groups=['admin', 'user'])
tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'user'])

agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=user_resolver,
    agent_memory=agent_memory,
    system_prompt_builder=CustomSystemPromptBuilder() 
)

print("vanna setup successfully")
