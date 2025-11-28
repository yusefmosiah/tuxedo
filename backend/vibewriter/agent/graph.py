from typing import Annotated, List, TypedDict, Union, Literal
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

# Tools
from backend.vibewriter.tools.core import TerminalTool, FileReadTool, FileWriteTool, FileListTool
from backend.vibewriter.tools.choir import SearchChoirKnowledgeBase, PublishToChoir, CiteArticle
from backend.vibewriter.sandbox.era_sandbox import EraSandbox

# Defines the State of our Deep Agent
class AgentState(TypedDict):
    messages: List[BaseMessage]
    plan: List[str]  # High-level plan/todos
    current_step: int
    scratchpad: str

# ------------------------------------------------------------------------------
# THE VIBEWRITER DEEP AGENT
# ------------------------------------------------------------------------------

class VibewriterAgent:
    def __init__(self, vm_id: str, model_name: str = "claude-3-5-sonnet-20241022"):
        # 1. Initialize Sandbox
        self.sandbox = EraSandbox(vm_id)

        # 2. Initialize Tools
        # Core "Computer Control" Tools
        self.core_tools = [
            TerminalTool(sandbox=self.sandbox),
            FileReadTool(sandbox=self.sandbox),
            FileWriteTool(sandbox=self.sandbox),
            FileListTool(sandbox=self.sandbox),
        ]

        # Domain "Choir" Tools
        self.choir_tools = [
            SearchChoirKnowledgeBase(),
            PublishToChoir(),
            CiteArticle()
        ]

        self.all_tools = self.core_tools + self.choir_tools
        self.tool_node = ToolNode(self.all_tools)

        # 3. Initialize LLM
        # We assume standard environment variables (ANTHROPIC_API_KEY) are set
        self.llm = ChatAnthropic(model=model_name).bind_tools(self.all_tools)

        # 4. Build the Graph
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Nodes
        workflow.add_node("planner", self._plan_node)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self.tool_node)

        # Edges
        workflow.add_edge(START, "planner")
        workflow.add_edge("planner", "agent")

        # Conditional edge from agent: Tools or End?
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )

        workflow.add_edge("tools", "agent")

        return workflow.compile()

    # --------------------------------------------------------------------------
    # NODE IMPLEMENTATIONS
    # --------------------------------------------------------------------------

    def _plan_node(self, state: AgentState):
        """
        The Planner Node.
        If no plan exists, generates the '8-stage Ghostwriter' plan.
        """
        if state.get("plan"):
            return {} # Plan already exists

        # Default Ghostwriter/Vibewriter Plan Template
        initial_plan = [
            "1. Form Hypotheses: Analyze the topic and generate 3-5 competing hypotheses.",
            "2. Experimental Design: Create a search plan to test these hypotheses.",
            "3. Research: Use the terminal/browser to gather evidence (save to 02_evidence/).",
            "4. Update Certitudes: Evaluate evidence and update hypothesis confidence.",
            "5. Thesis Draft: Write a comprehensive draft based on the strongest hypotheses.",
            "6. Verification: Check all citations in the draft.",
            "7. Publish: If verification passes, publish to Choir.",
        ]

        return {"plan": initial_plan, "current_step": 0}

    def _agent_node(self, state: AgentState):
        """
        The Core Agent Node.
        Decides the next action based on the Plan and Messages.
        """
        messages = state["messages"]
        plan = state["plan"]
        current_step_idx = state.get("current_step", 0)

        if current_step_idx >= len(plan):
            return {"messages": [AIMessage(content="All steps completed.")]}

        current_task = plan[current_step_idx]

        # System Prompt injecting the Persona and Plan
        system_prompt = f"""You are Vibewriter, an autonomous research agent.
You have full access to a computer (sandbox) via terminal and file tools.
You also have access to the Choir platform via specific tools.

Current Plan:
{chr(10).join(plan)}

Your Current Task: {current_task}

Execute this task using your tools.
When the task is complete, output a message starting with "STEP COMPLETE: <summary>".
"""

        # We prepend the system prompt to the history
        # (In a real app, we'd manage context window better)
        response = self.llm.invoke([HumanMessage(content=system_prompt)] + messages)

        return {"messages": [response]}

    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        messages = state["messages"]
        last_message = messages[-1]

        # If the LLM made tool calls, execute them
        if last_message.tool_calls:
            return "continue"

        # If the LLM thinks the step is done (heuristic check)
        if "STEP COMPLETE" in str(last_message.content):
            # TODO: Logic to advance 'current_step' would go here in a more complex graph
            # For now, we just end the turn, but in a real loop we'd loop back to planner/agent
            return "end"

        return "end" # Default stop if no tools and no explicit completion (conversation turn)

# Helper to run
async def run_vibewriter(topic: str, vm_id: str):
    agent = VibewriterAgent(vm_id)
    initial_state = {
        "messages": [HumanMessage(content=f"Research topic: {topic}")],
        "plan": [],
        "current_step": 0,
        "scratchpad": ""
    }

    async for event in agent.graph.astream(initial_state):
        for key, value in event.items():
            print(f"--- Node: {key} ---")
            # print(value)
