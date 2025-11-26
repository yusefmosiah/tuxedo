"""
Hypothesis Formation Tool - Stage 1 work node.

Generates testable hypotheses with initial certitude scores based on
general knowledge (no web research at this stage).

Usage:
    tool = FormHypothesesTool(aws_region="us-east-1")
    result = await tool.run(
        topic="Ethereum Layer 2 scaling solutions",
        session_id="session_20251126_040000",
        user_id="alice"
    )

Data Flow:
    Inputs: topic (string), session_id, user_id
    Outputs: 00_hypotheses/initial_hypotheses.json
    Dependencies: None (first stage in workflow)
"""

import asyncio
import json
from typing import Optional
from datetime import datetime

from openhands.sdk import Agent, Conversation, Tool
from openhands.tools.file_editor import FileEditorTool

from .base import GhostwriterToolBase, ToolResult


class FormHypothesesTool(GhostwriterToolBase):
    """
    Form research hypotheses with certitude scores.

    This tool creates multiple competing hypotheses about a topic,
    each with an initial certitude score based on general knowledge.
    No web research is performed at this stage - that comes later in
    the experimental design phase.

    The agent is instructed to generate 3-7 testable hypotheses that are:
    - Specific enough to be falsifiable
    - Broad enough to guide comprehensive research
    - Scored with initial certitude (0.0-1.0) based on general knowledge

    Output Format:
        {
            "topic": "...",
            "date_generated": "YYYY-MM-DD",
            "hypotheses": [
                {
                    "id": 1,
                    "hypothesis": "...",
                    "initial_certitude": 0.5,
                    "reasoning": "..."
                },
                ...
            ]
        }
    """

    name = "form_hypotheses"
    description = "Generate testable research hypotheses with initial certitude scores"

    async def run(
        self,
        topic: str,
        session_id: str,
        user_id: str = "default",
        num_hypotheses: int = 5
    ) -> ToolResult:
        """
        Execute hypothesis formation.

        Args:
            topic: Research topic (e.g., "DeFi lending protocols")
            session_id: Workspace session identifier
            user_id: User identifier for multi-tenant isolation
            num_hypotheses: Target number of hypotheses (3-7)

        Returns:
            ToolResult with path to hypotheses file
        """

        # Get workspace
        workspace_dir, workspace = self.get_workspace(user_id, session_id)

        # Ensure output directory exists
        self.ensure_output_dir(workspace_dir, "00_hypotheses")

        # Create hypothesis former sub-agent (using Sonnet for quality)
        former_llm = self.create_llm(self.SONNET)
        former = Agent(
            llm=former_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(agent=former, workspace=workspace)

        # Load and format prompt
        try:
            prompt = self.load_prompt(
                "hypothesis_former.txt",
                topic=topic,
                date_accessed=datetime.now().strftime("%Y-%m-%d"),
                num_hypotheses=num_hypotheses
            )
        except FileNotFoundError:
            # Fallback prompt if template doesn't exist yet
            prompt = self._get_fallback_prompt(topic, num_hypotheses)

        # Send message to agent
        conv.send_message(prompt)

        # Run to completion (in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conv.run)

        # Verify output
        output_path = "00_hypotheses/initial_hypotheses.json"
        success, error = self.verify_output(workspace_dir, output_path)

        if not success:
            return ToolResult(
                success=False,
                output="Hypothesis formation failed",
                error=error
            )

        # Parse and extract metadata
        output_full_path = workspace_dir / output_path
        with open(output_full_path) as f:
            data = json.load(f)

        num_generated = len(data.get("hypotheses", []))
        avg_certitude = sum(
            h.get("initial_certitude", 0.5)
            for h in data.get("hypotheses", [])
        ) / max(num_generated, 1)

        return ToolResult(
            success=True,
            output=f"Generated {num_generated} hypotheses (avg certitude: {avg_certitude:.2f})",
            output_path=output_path,
            metadata={
                "num_hypotheses": num_generated,
                "avg_certitude": avg_certitude,
                "session_id": session_id,
                "topic": topic
            }
        )

    def _get_fallback_prompt(self, topic: str, num_hypotheses: int) -> str:
        """
        Fallback prompt if template file doesn't exist yet.
        This allows tool to work before all prompts are migrated.
        """
        return f"""You are a research hypothesis former. Generate {num_hypotheses} testable hypotheses about: {topic}

For each hypothesis:
1. Make it specific and falsifiable
2. Assign an initial certitude score (0.0-1.0) based on your general knowledge
3. Explain your reasoning for the certitude score

Output the hypotheses to a JSON file: 00_hypotheses/initial_hypotheses.json

Use this exact format:
{{
    "topic": "{topic}",
    "date_generated": "{datetime.now().strftime('%Y-%m-%d')}",
    "hypotheses": [
        {{
            "id": 1,
            "hypothesis": "Your hypothesis text here",
            "initial_certitude": 0.5,
            "reasoning": "Why you assigned this certitude"
        }},
        ...
    ]
}}

Use the FileEditorTool to create the file. Be thorough and thoughtful.
"""
