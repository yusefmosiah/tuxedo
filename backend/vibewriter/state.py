from typing import Annotated, List, Optional, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class Citation(TypedDict):
    url: str
    title: str
    snippet: Optional[str]

class VibewriterState(TypedDict):
    # Standard LangGraph messages
    messages: Annotated[List[BaseMessage], add_messages]

    # Vibewriter specific state
    research_notes: str
    draft_content: str
    citations: List[Citation]
    current_phase: str # "research", "writing", "review", "publishing"
