"""
Autonomous Ghostwriter Orchestrator.

Unlike the linear pipeline, this orchestrator gives the agent full autonomy
to decide:
- Which tools to call and in what order
- When to loop back to earlier stages (e.g., revise hypotheses)
- When to skip stages that aren't needed
- When research is complete

The agent learns optimal workflows over time (Phase 2: vector DB integration).

Architecture:
    User Request → AutonomousGhostwriter → Agent (Sonnet)
                                              ↓
                                         Tool Nodes
                                    (hypotheses, research, draft, etc.)
                                              ↓
                                          Workspace
                                      (persistent files)

Key Differences from Pipeline:
    - Agent decides workflow (not hardcoded sequence)
    - User can intervene at any time via conversation
    - Streams progress to frontend
    - (Phase 2) Learns from experience via vector DB
"""

import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from openhands.sdk import Agent, LLM, Conversation, Tool
from openhands.workspace import LocalWorkspace

from backend.utils.path_manager import PersistentPathManager

# Import tool nodes as they're implemented
from .tools.hypothesis_former import FormHypothesesTool
from .tools.hypothesis_revisor import RevisitHypothesesTool


class AutonomousGhostwriter:
    """
    Self-directed research agent with tool-based workflow.

    The agent autonomously decides which tools to use, in what order,
    based on:
    - Research quality requirements
    - Evidence quality
    - (Phase 2) Learned patterns from similar past research

    User can intervene at any time via natural language.

    Example Usage:
        orchestrator = AutonomousGhostwriter(user_id="alice")

        async for event in orchestrator.research_streaming("DeFi protocols"):
            if event["type"] == "message":
                print(f"Agent: {event['content']}")
            elif event["type"] == "tool_call":
                print(f"Calling: {event['tool_name']}")
            elif event["type"] == "complete":
                print(f"Done! Report at: {event['workspace_dir']}")
    """

    # Model identifiers
    SONNET = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    HAIKU = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    def __init__(
        self,
        aws_region: str = "us-east-1",
        user_id: str = "default",
        enable_learning: bool = False  # Phase 2: vector DB learning
    ):
        """
        Initialize autonomous orchestrator.

        Args:
            aws_region: AWS region for Bedrock
            user_id: User identifier for multi-tenant workspace isolation
            enable_learning: Enable vector DB pattern learning (Phase 2)
        """
        self.aws_region = aws_region
        self.user_id = user_id
        self.enable_learning = enable_learning

        # Initialize tool nodes
        # As we implement more tools, add them here
        self.tool_instances = [
            FormHypothesesTool(aws_region=aws_region),
            RevisitHypothesesTool(aws_region=aws_region),
            # TODO: Add more tools as implemented:
            # DesignExperimentsTool,
            # ExecuteWebResearchTool,
            # etc.
        ]

        # Phase 2: Vector DB for learning
        self.memory = None
        if enable_learning:
            # Will implement in Phase 2
            # from backend.memory.vector_store import ResearchMemory
            # self.memory = ResearchMemory()
            pass

    def create_session(self, topic: str) -> str:
        """
        Create workspace for research session.

        Args:
            topic: Research topic

        Returns:
            Session ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"

        # Get persistent workspace directory
        workspace_dir = PersistentPathManager.workspace_dir(
            user_id=self.user_id,
            session_id=session_id
        )

        # Create stage directories (same structure as pipeline for compatibility)
        stage_dirs = [
            "00_hypotheses",
            "01_experimental_design",
            "02_evidence",
            "03_updated_hypotheses",
            "04_draft",
            "05_verification",
            "06_revision",
            "07_final"
        ]

        for dir_name in stage_dirs:
            (workspace_dir / dir_name).mkdir(parents=True, exist_ok=True)

        # Save session metadata
        metadata = {
            "session_id": session_id,
            "user_id": self.user_id,
            "topic": topic,
            "created_at": timestamp,
            "mode": "autonomous",  # vs "pipeline" for old implementation
            "workspace_dir": str(workspace_dir)
        }

        metadata_path = workspace_dir / "session_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))

        return session_id

    def create_llm(self, model: str) -> LLM:
        """
        Create LLM instance with Bedrock configuration.

        Args:
            model: Model ID (SONNET or HAIKU constant)

        Returns:
            Configured LLM instance
        """
        import os

        # Get AWS credentials from environment
        bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        # Construct full model name with bedrock/ prefix
        full_model_name = f"bedrock/{model}"

        if bearer_token:
            return LLM(
                model=full_model_name,
                api_key=bearer_token,
                aws_region_name=self.aws_region
            )
        elif access_key and secret_key:
            return LLM(
                model=full_model_name,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_region_name=self.aws_region
            )
        else:
            raise ValueError(
                "AWS Bedrock credentials not configured. Set either:\\n"
                "  1. AWS_BEARER_TOKEN_BEDROCK (recommended)\\n"
                "  2. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY"
            )

    def get_system_prompt(self, topic: str, session_id: str) -> str:
        """
        Generate system prompt for autonomous research agent.

        Phase 1: Basic orchestration instructions
        Phase 2: Will include learned patterns from vector DB

        Args:
            topic: Research topic
            session_id: Session identifier

        Returns:
            System prompt string
        """

        # Get tool descriptions
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tool_instances
        ])

        # Phase 2: Recall learned patterns from vector DB
        learned_insights = ""
        if self.memory:
            # TODO: Implement in Phase 2
            # patterns = self.memory.recall_similar_patterns(topic, limit=3)
            # learned_insights = self._format_learned_patterns(patterns)
            pass

        return f"""You are an autonomous research agent with expertise in hypothesis-driven research methodology.

RESEARCH TOPIC: {topic}
SESSION ID: {session_id}

AVAILABLE TOOLS:
{tool_descriptions}

WORKFLOW PHILOSOPHY:
You are NOT following a fixed pipeline. You have full autonomy to decide:
1. Which tools to call and in what order
2. When to loop back to earlier stages (e.g., revisit_hypotheses if evidence is weak)
3. When to skip stages that aren't needed for this specific research
4. When research quality is sufficient to complete

DECISION FRAMEWORK:
- Start with form_hypotheses to establish testable claims
- Design targeted experiments to test hypotheses
- Gather evidence through web research
- IMPORTANT: If evidence quality is poor or contradicts hypotheses,
  consider calling revisit_hypotheses rather than forcing ahead
- Only draft when hypotheses have sufficient supporting evidence (certitude ≥ 0.6)
- Always verify citations before finalizing report
- Ask user for guidance if genuinely unsure about next step

USER INTERACTION:
- Stream your thinking process ("Forming hypotheses...", "Evidence suggests X...")
- Ask user for approval before major decisions (e.g., "Ready to draft?" or "Evidence is weak, should I revise hypotheses?")
- Allow user to inspect workspace at any time (e.g., "show me the hypotheses")
- User can redirect you at any point - be responsive to their guidance

QUALITY OVER SPEED:
Take the time needed to produce excellent research. It's better to loop back and
revise hypotheses than to force a draft from weak or contradictory evidence.
Your goal is research quality, not completing stages quickly.

{learned_insights}

Begin by announcing your research plan in 1-2 sentences, then call form_hypotheses to start.
"""

    async def research_streaming(
        self,
        topic: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Start autonomous research with streaming progress.

        Yields events:
            {"type": "thinking", "content": "..."}
            {"type": "tool_call", "tool": "form_hypotheses", "args": {...}}
            {"type": "tool_result", "tool": "form_hypotheses", "result": {...}}
            {"type": "message", "content": "Assistant message"}
            {"type": "complete", "session_id": "...", "workspace_dir": "..."}

        User can intervene via send_message() on the returned conversation.

        Args:
            topic: Research topic

        Yields:
            Progress events (dict)
        """

        # Create session
        session_id = self.create_session(topic)
        start_time = time.time()

        # Track tool calls for learning (Phase 2)
        tool_sequence: List[str] = []

        try:
            # Get workspace
            workspace_dir = PersistentPathManager.workspace_dir(
                self.user_id, session_id
            )
            workspace = LocalWorkspace(base_dir=str(workspace_dir))

            # Create autonomous agent with tools
            llm = self.create_llm(self.SONNET)

            # Convert tool instances to OpenHands Tool objects
            # Note: This is a simplified approach for Phase 1
            # In production, we'd use proper tool registration
            openhands_tools = [
                Tool(name=tool.name, description=tool.description)
                for tool in self.tool_instances
            ]

            agent = Agent(llm=llm, tools=openhands_tools)

            # Create conversation
            conv = Conversation(agent=agent, workspace=workspace)

            # Send system prompt
            system_prompt = self.get_system_prompt(topic, session_id)
            conv.send_message(system_prompt)

            # Yield initial event
            yield {
                "type": "session_created",
                "session_id": session_id,
                "topic": topic,
                "workspace_dir": str(workspace_dir)
            }

            # Stream conversation events
            # Note: This is pseudocode - actual OpenHands SDK streaming API may differ
            # We'll refine this based on SDK documentation
            for event in conv.run_streaming():
                # Track tool calls for learning
                if hasattr(event, 'tool_name'):
                    tool_sequence.append(event.tool_name)

                # Transform SDK event to our format
                yield {
                    "type": getattr(event, "type", "message"),
                    "content": getattr(event, "content", ""),
                    "tool_name": getattr(event, "tool_name", None),
                    "session_id": session_id
                }

            # Calculate execution metrics
            execution_time = time.time() - start_time

            # Phase 2: Store learned pattern
            if self.memory and tool_sequence:
                # TODO: Implement pattern storage
                # outcome_quality = self._assess_outcome_quality(session_id)
                # self.memory.store_pattern(...)
                pass

            # Final completion event
            yield {
                "type": "complete",
                "session_id": session_id,
                "workspace_dir": str(workspace_dir),
                "execution_time_seconds": execution_time,
                "tool_sequence": tool_sequence
            }

        except Exception as e:
            yield {
                "type": "error",
                "session_id": session_id,
                "error": str(e)
            }
            raise

    # Phase 2 methods (placeholders for now)

    def _assess_outcome_quality(self, session_id: str) -> float:
        """
        Assess quality of research outcome.
        Phase 2: Implement quality metrics.

        Returns:
            Quality score 0.0-1.0
        """
        # TODO: Implement in Phase 2
        # - Check final report exists
        # - Check average certitude of hypotheses
        # - Check citation verification rate
        # - Check evidence quality
        return 0.8  # Placeholder

    def _categorize_topic(self, topic: str) -> str:
        """
        Categorize topic for pattern matching.
        Phase 2: Implement topic classification.

        Returns:
            Category string (e.g., "blockchain", "defi", "ai")
        """
        # TODO: Implement in Phase 2
        # Use LLM or embedding-based classification
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ["defi", "protocol", "blockchain", "ethereum", "stellar"]):
            return "blockchain"
        return "general"
