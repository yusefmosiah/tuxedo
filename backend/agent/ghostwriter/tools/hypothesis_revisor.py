"""
Hypothesis Revision Tool - Meta-cognitive work node.

Allows agent to revise hypotheses based on evidence gathered so far.
This enables non-linear workflow - the agent can loop back to hypothesis
formation after discovering that current hypotheses are insufficient.

Usage:
    tool = RevisitHypothesesTool(aws_region="us-east-1")
    result = await tool.run(
        session_id="session_20251126_040000",
        user_id="alice",
        revision_reason="Evidence contradicts initial assumptions"
    )

Data Flow:
    Inputs: session_id, user_id, revision_reason
    Reads: 00_hypotheses/initial_hypotheses.json (or latest version)
    Reads: 02_evidence/*.md (if available)
    Outputs: 00_hypotheses/revised_hypotheses_v{N}.json
"""

import asyncio
import json
from typing import Optional
from datetime import datetime
from pathlib import Path

from openhands.sdk import Agent, Conversation, Tool
from openhands.tools.file_editor import FileEditorTool

from .base import GhostwriterToolBase, ToolResult


class RevisitHypothesesTool(GhostwriterToolBase):
    """
    Revise research hypotheses based on new insights.

    This is a meta-cognitive tool that allows the autonomous agent to
    loop back and revise its hypotheses when:
    - Evidence contradicts initial hypotheses
    - New angle emerges from research
    - Hypothesis is too broad or too narrow
    - Certitude scores suggest hypothesis needs refinement

    The tool reads:
    - Previous hypotheses (all versions)
    - Evidence gathered so far
    - Certitude updates

    And generates:
    - Revised hypotheses with version increment
    - Explanation of what changed and why
    """

    name = "revisit_hypotheses"
    description = "Revise research hypotheses based on evidence and new insights"

    async def run(
        self,
        session_id: str,
        user_id: str = "default",
        revision_reason: str = "Evidence suggests revision needed"
    ) -> ToolResult:
        """
        Execute hypothesis revision.

        Args:
            session_id: Workspace session identifier
            user_id: User identifier
            revision_reason: Why hypotheses need revision (for agent context)

        Returns:
            ToolResult with path to revised hypotheses
        """

        # Get workspace
        workspace_dir, workspace = self.get_workspace(user_id, session_id)

        # Find current hypothesis version
        hypothesis_dir = workspace_dir / "00_hypotheses"
        if not hypothesis_dir.exists():
            return ToolResult(
                success=False,
                output="Cannot revise - no initial hypotheses found",
                error="00_hypotheses directory does not exist"
            )

        # Get latest hypothesis version
        current_version, current_path = self._get_latest_hypothesis_version(
            hypothesis_dir
        )

        if not current_path:
            return ToolResult(
                success=False,
                output="Cannot revise - no hypothesis files found",
                error="No hypothesis JSON files in 00_hypotheses/"
            )

        # Load current hypotheses
        with open(current_path) as f:
            current_hypotheses = json.load(f)

        # Load evidence if available
        evidence_summary = self._load_evidence_summary(workspace_dir)

        # Create revisor sub-agent (using Sonnet for quality)
        revisor_llm = self.create_llm(self.SONNET)
        revisor = Agent(
            llm=revisor_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(agent=revisor, workspace=workspace)

        # Create revision prompt
        prompt = self._get_revision_prompt(
            current_hypotheses=current_hypotheses,
            evidence_summary=evidence_summary,
            revision_reason=revision_reason,
            next_version=current_version + 1
        )

        conv.send_message(prompt)

        # Run to completion
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conv.run)

        # Verify output
        next_version = current_version + 1
        output_path = f"00_hypotheses/revised_hypotheses_v{next_version}.json"
        success, error = self.verify_output(workspace_dir, output_path)

        if not success:
            return ToolResult(
                success=False,
                output="Hypothesis revision failed",
                error=error
            )

        # Parse revised hypotheses
        with open(workspace_dir / output_path) as f:
            revised = json.load(f)

        num_hypotheses = len(revised.get("hypotheses", []))
        changes = revised.get("revision_summary", {}).get("changes_made", [])

        return ToolResult(
            success=True,
            output=f"Revised to {num_hypotheses} hypotheses (v{next_version})",
            output_path=output_path,
            metadata={
                "version": next_version,
                "num_hypotheses": num_hypotheses,
                "changes_made": len(changes),
                "revision_reason": revision_reason
            }
        )

    def _get_latest_hypothesis_version(
        self,
        hypothesis_dir: Path
    ) -> tuple[int, Optional[Path]]:
        """
        Find the latest hypothesis version.

        Returns:
            (version_number, path_to_file)
        """
        # Check for initial hypotheses
        initial_path = hypothesis_dir / "initial_hypotheses.json"
        if initial_path.exists() and not list(hypothesis_dir.glob("revised_hypotheses_v*.json")):
            return 0, initial_path

        # Find highest version number
        version_files = list(hypothesis_dir.glob("revised_hypotheses_v*.json"))
        if not version_files:
            return 0, initial_path if initial_path.exists() else None

        # Extract version numbers and find max
        versions = []
        for f in version_files:
            try:
                v = int(f.stem.split("_v")[1])
                versions.append((v, f))
            except (IndexError, ValueError):
                continue

        if not versions:
            return 0, initial_path if initial_path.exists() else None

        max_version, max_path = max(versions, key=lambda x: x[0])
        return max_version, max_path

    def _load_evidence_summary(self, workspace_dir: Path) -> str:
        """Load summary of evidence gathered so far."""
        evidence_dir = workspace_dir / "02_evidence"
        if not evidence_dir.exists():
            return "No evidence gathered yet."

        evidence_files = list(evidence_dir.glob("evidence_hypothesis_*.md"))
        if not evidence_files:
            return "No evidence files found yet."

        # Create brief summary
        summaries = []
        for i, file in enumerate(evidence_files[:3], 1):  # Limit to first 3
            content = file.read_text()[:500]  # First 500 chars
            summaries.append(f"Evidence file {i}: {content}...")

        return "\n\n".join(summaries)

    def _get_revision_prompt(
        self,
        current_hypotheses: dict,
        evidence_summary: str,
        revision_reason: str,
        next_version: int
    ) -> str:
        """Generate revision prompt for agent."""

        hypotheses_text = json.dumps(current_hypotheses, indent=2)

        return f"""You are revising research hypotheses based on new insights.

CURRENT HYPOTHESES (version {next_version - 1}):
{hypotheses_text}

EVIDENCE GATHERED SO FAR:
{evidence_summary}

REASON FOR REVISION:
{revision_reason}

TASK:
Revise the hypotheses based on the evidence and insights. You may:
- Modify existing hypotheses to be more specific/refined
- Add new hypotheses if evidence suggests new angles
- Remove hypotheses that have been falsified
- Adjust certitude scores based on evidence

Output the revised hypotheses to: 00_hypotheses/revised_hypotheses_v{next_version}.json

Use this format:
{{
    "topic": "{current_hypotheses.get('topic', 'Unknown')}",
    "date_revised": "{datetime.now().strftime('%Y-%m-%d')}",
    "version": {next_version},
    "previous_version": {next_version - 1},
    "revision_summary": {{
        "reason": "{revision_reason}",
        "changes_made": [
            "Description of change 1",
            "Description of change 2"
        ]
    }},
    "hypotheses": [
        {{
            "id": 1,
            "hypothesis": "Revised hypothesis text",
            "initial_certitude": 0.X,
            "reasoning": "Why this certitude, how it changed"
        }},
        ...
    ]
}}

Use the FileEditorTool to create the file. Explain your reasoning for each revision.
"""
