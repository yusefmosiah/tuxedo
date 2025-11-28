import os
from typing import Any, Dict, Optional, Sequence

from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain.agents.middleware.summarization import SummarizationMiddleware
from langchain_anthropic import ChatAnthropic
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware

from .runloop_backend import RunloopBackend
from .subagents.researcher import get_researcher_agent
from .subagents.writer import get_writer_agent
from .subagents.ghostwriter import get_ghostwriter_agent
from .tools import get_vibewriter_tools

class VibewriterAgent:
    """Vibewriter Deep Agent using Runloop backend and manual subagents."""

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        devbox_id: Optional[str] = None,
    ):
        self.backend = RunloopBackend(api_key=api_key, devbox_id=devbox_id)

        # Model setup
        if os.environ.get("ANTHROPIC_API_KEY"):
            self.model = ChatAnthropic(model_name=model_name)
            self.is_anthropic = True
        elif os.environ.get("OPENAI_API_KEY"):
            from langchain_openai import ChatOpenAI
            base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
            or_model = "anthropic/claude-3.5-sonnet"
            self.model = ChatOpenAI(
                model=or_model,
                api_key=os.environ.get("OPENAI_API_KEY"),
                base_url=base_url
            )
            self.is_anthropic = False
        else:
            raise ValueError("No API key found for Anthropic or OpenAI/OpenRouter")

        # Initialize subagents
        self.researcher = self._create_subagent(get_researcher_agent())
        self.writer = self._create_subagent(get_writer_agent())
        self.ghostwriter = self._create_subagent(get_ghostwriter_agent())

        # Tools setup
        self.tools = self._setup_tools()

        # Middleware setup
        middleware = [
            TodoListMiddleware(),
            SummarizationMiddleware(
                model=self.model,
                max_tokens_before_summary=170000,
                messages_to_keep=6,
            ),
            PatchToolCallsMiddleware(),
        ]

        if self.is_anthropic:
            middleware.append(AnthropicPromptCachingMiddleware(unsupported_model_behavior="ignore"))

        # Create main agent
        system_prompt = (
            "You are Vibewriter, a financial delegate agent. You have access to a secure sandbox environment.\n"
            "You can list, read, write files and execute commands.\n"
            "You also have specialized sub-agents: 'research_task', 'writing_task', 'ghostwriter_task'.\n"
            "You have tools to manage Stellar accounts: 'agent_create_account', 'agent_list_accounts', 'agent_get_account_info'.\n"
            "Delegate complex research or writing tasks to sub-agents.\n"
            "Always verify your actions."
        )

        self.graph = create_agent(
            self.model,
            system_prompt=system_prompt,
            tools=self.tools,
            middleware=middleware,
        ).with_config({"recursion_limit": 1000})

    def _create_subagent(self, config: Dict[str, Any]):
        """Helper to create a subagent from config."""
        return create_agent(
            self.model,
            system_prompt=config["system_prompt"],
            tools=config["tools"],
            middleware=[PatchToolCallsMiddleware()],
        )

    def _setup_tools(self):
        @tool
        def ls(path: str) -> str:
            """List files in a directory. Path must be absolute."""
            if not path.startswith("/"):
                return "Error: Path must be absolute (start with /)"
            return str(self.backend.ls_info(path))

        @tool
        def read_file(path: str) -> str:
            """Read a file. Path must be absolute."""
            if not path.startswith("/"):
                return "Error: Path must be absolute (start with /)"
            return self.backend.read(path)

        @tool
        def write_file(path: str, content: str) -> str:
            """Write a file. Path must be absolute."""
            if not path.startswith("/"):
                return "Error: Path must be absolute (start with /)"
            res = self.backend.write(path, content)
            if res.error:
                return f"Error: {res.error}"
            return f"Successfully wrote to {path}"

        @tool
        def execute(command: str) -> str:
            """Execute a shell command."""
            res = self.backend.execute(command)
            return f"Exit Code: {res.exit_code}\nOutput:\n{res.output}"

        @tool
        def research_task(description: str) -> str:
            """Delegate a research task to the Researcher agent.
            Use this for finding information, checking prices, or searching the KB.
            """
            try:
                result = self.researcher.invoke({"messages": [HumanMessage(content=description)]})
                # Extract the last message content
                if result["messages"]:
                    return result["messages"][-1].content
                return "No response from researcher."
            except Exception as e:
                return f"Error in researcher: {e}"

        @tool
        def writing_task(description: str) -> str:
            """Delegate a writing task to the Writer agent.
            Use this for drafting content, citing sources, and publishing.
            """
            try:
                result = self.writer.invoke({"messages": [HumanMessage(content=description)]})
                if result["messages"]:
                    return result["messages"][-1].content
                return "No response from writer."
            except Exception as e:
                return f"Error in writer: {e}"

        @tool
        def ghostwriter_task(description: str) -> str:
            """Delegate a hypothesis formation or revision task to the Ghostwriter agent.
            Use this for creating or updating research hypotheses.
            """
            try:
                result = self.ghostwriter.invoke({"messages": [HumanMessage(content=description)]})
                if result["messages"]:
                    return result["messages"][-1].content
                return "No response from ghostwriter."
            except Exception as e:
                return f"Error in ghostwriter: {e}"

        return [ls, read_file, write_file, execute, research_task, writing_task, ghostwriter_task] + get_vibewriter_tools()

    def invoke(self, input_text: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invoke the agent with a user message."""
        messages = [HumanMessage(content=input_text)]
        config = config or {}
        return self.graph.invoke({"messages": messages}, config=config)

    def cleanup(self):
        """Shutdown the backend resources."""
        self.backend.shutdown()
