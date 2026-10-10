from langchain.agents import create_agent
from agent.interrupt_middleware import ClarificationInterruptMiddleware, ask_user
from agent.prompts_library import SYSTEM_PROMPTS
from memory.short_term import ShortTermMemory
from db_store import DatabaseStore
from llm.factory import get_llm, get_small_llm
from observability.logger import get_logger

logger = get_logger(__name__)
def build_req_agent():
    """Create and return a Langchain requirement agent with persistent memory."""
    memory = None
    database = None
    try:
        llm = get_llm()
        database = DatabaseStore()
        memory = ShortTermMemory(database.pool)
        agent = create_agent(
            llm,
            system_prompt=SYSTEM_PROMPTS["requirements"],
            tools=[ask_user],
            checkpointer=memory.checkpointer,
            middleware=[
                ShortTermMemory.get_summarization_middleware(),
                ClarificationInterruptMiddleware(),
            ]
        )
    except Exception as e:
        print(f"Error occurred while building the agent. Closing memory. {e}")
        if database:
            database.close()
        raise
    return agent, memory, database

# def build_small_llm():
#     """Create and return a small Langchain agent"""
#     try:
#         llm = get_small_llm()
#         agent = create_agent(
#         llm
#         )
#     except Exception as e:
#         print(f"Error occurred while building the agent. Closing memory. {e}")
#     return agent