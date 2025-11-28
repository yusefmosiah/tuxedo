import os
from typing import Literal

from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# Import our custom Backend
from backend.vibewriter.sandbox.era_backend import EraBackend
# Import Choir Tools
from backend.vibewriter.tools.choir import SearchChoirKnowledgeBase, PublishToChoir, CiteArticle

def create_vibewriter_agent(vm_id: str, model_name: str = "claude-3-5-sonnet-20241022"):
    """
    Creates a Vibewriter Deep Agent connected to a specific ERA MicroVM.
    """

    # 1. Initialize the Custom ERA Backend (Filesystem Bridge)
    era_backend = EraBackend(vm_id=vm_id)

    # 2. Define Tools
    # Note: DeepAgents comes with built-in filesystem/planning tools.
    # We add our domain-specific Choir tools.
    tools = [
        SearchChoirKnowledgeBase(),
        PublishToChoir(),
        CiteArticle()
    ]

    # 3. Define System Prompt
    system_prompt = """You are Vibewriter, an autonomous research agent for the Choir platform.
Your goal is to conduct high-quality research, verify facts, and publish novel content.

You have access to:
1. A full Linux environment (via your filesystem tools) where you can read/write files and run scripts.
2. The Choir knowledge base (search_choir_kb).
3. The Choir publishing system (publish_to_choir, cite_article).

Process:
1. PLAN: Always use your planning tool to break down complex research topics.
2. RESEARCH: Use the filesystem to save your notes. Search the Choir KB.
3. DRAFT: Write your draft in markdown files (e.g., `draft.md`).
4. VERIFY: Double-check your citations.
5. PUBLISH: When ready, use `publish_to_choir`.

You are a "Deep Agent" - you should think deeply, plan extensively, and manage your own memory in the filesystem.
"""

    # 4. Create the Agent
    # We inject our custom backend as the 'filesystem' for the agent.
    # This means when the agent uses 'read_file' or 'write_file', it goes to the MicroVM.
    agent = create_deep_agent(
        model=ChatAnthropic(model=model_name),
        tools=tools,
        system_prompt=system_prompt,
        backend=era_backend
    )

    return agent

# Example Runner
async def run_vibewriter_task(topic: str, vm_id: str):
    agent = create_vibewriter_agent(vm_id)

    # Invoke the agent
    result = await agent.ainvoke({
        "messages": [HumanMessage(content=f"Please research and write a report on: {topic}")]
    })

    return result
