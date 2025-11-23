"""
Ghostwriter Pipeline Implementation using OpenHands SDK

This module implements the 8-stage research and writing pipeline using OpenHands SDK
with AWS Bedrock Claude 4.5 models (Haiku and Sonnet).

Architecture: docs/GHOSTWRITER_ARCHITECTURE_OPENHANDS_SDK.md
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# OpenHands SDK imports
from openhands.sdk import Agent, LLM, Conversation, Tool, LocalWorkspace
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.terminal import TerminalTool

logger = logging.getLogger(__name__)


class GhostwriterPipeline:
    """
    Multi-stage research and writing pipeline using OpenHands SDK.

    Implements 8 stages:
    1. Research (Haiku subagents) - parallel web research
    2. Draft (Sonnet) - synthesis into coherent document
    3. Extract (Haiku) - atomic claims extraction
    4. Verify (Haiku) - 3-layer verification
    5. Critique (Sonnet) - quality assessment
    6. Revise (Sonnet) - fix unsupported claims
    7. Re-verify (Haiku) - verify revised claims
    8. Style (Sonnet) - apply style guide
    """

    # AWS Bedrock model IDs for Claude 4.5
    HAIKU = "anthropic.claude-haiku-4-5-20251001-v1:0"
    SONNET = "anthropic.claude-sonnet-4-5-20250929-v1:0"

    def __init__(
        self,
        workspace_root: str = "/workspace/ghostwriter_sessions",
        aws_region: str = "us-east-1",
        num_researchers: int = 5,
        max_revision_iterations: int = 3,
        verification_threshold: float = 0.90
    ):
        """
        Initialize Ghostwriter pipeline.

        Args:
            workspace_root: Root directory for session workspaces
            aws_region: AWS region for Bedrock
            num_researchers: Number of parallel research agents (3-10)
            max_revision_iterations: Maximum revision iterations (1-3)
            verification_threshold: Minimum verification rate (0.0-1.0)
        """
        self.workspace_root = Path(workspace_root)
        self.aws_region = aws_region
        self.num_researchers = num_researchers
        self.max_revision_iterations = max_revision_iterations
        self.verification_threshold = verification_threshold

        # Session tracking
        self.session_id: Optional[str] = None
        self.workspace: Optional[Path] = None

        # Create workspace root if needed
        self.workspace_root.mkdir(parents=True, exist_ok=True)

        logger.info(f"Ghostwriter pipeline initialized (region: {aws_region})")

    def create_session(self, topic: str) -> str:
        """
        Create new session workspace.

        Args:
            topic: Research topic

        Returns:
            Session ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"
        self.workspace = self.workspace_root / self.session_id

        # Create stage directories
        stage_dirs = [
            "00_research",
            "01_draft",
            "02_extraction",
            "03_verification",
            "04_critique",
            "05_revision",
            "06_re_verification",
            "07_style"
        ]

        for dir_name in stage_dirs:
            (self.workspace / dir_name).mkdir(parents=True, exist_ok=True)

        # Save session metadata
        metadata = {
            "session_id": self.session_id,
            "topic": topic,
            "created_at": timestamp,
            "num_researchers": self.num_researchers,
            "verification_threshold": self.verification_threshold
        }

        with open(self.workspace / "session_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Created session: {self.session_id}")
        return self.session_id

    def create_llm(self, model: str) -> LLM:
        """
        Create LLM instance with Bedrock configuration.

        Args:
            model: Model ID (HAIKU or SONNET constant - without bedrock/ prefix)

        Returns:
            Configured LLM instance

        Note:
            OpenHands SDK uses LiteLLM under the hood. Bedrock models require:
            - Model name with "bedrock/" prefix
            - AWS credentials as direct parameters (not via provider field)
            - Parameter name is "aws_region_name" not "aws_region"
        """
        import os

        # Get AWS credentials from environment
        bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        # Construct full model name with bedrock/ prefix
        full_model_name = f"bedrock/{model}"

        if bearer_token:
            # Bearer token auth (simpler, recommended)
            return LLM(
                model=full_model_name,
                api_key=bearer_token,
                aws_region_name=self.aws_region
            )
        elif access_key and secret_key:
            # IAM credentials auth (traditional)
            return LLM(
                model=full_model_name,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_region_name=self.aws_region
            )
        else:
            raise ValueError(
                "AWS Bedrock credentials not configured. Set either:\n"
                "  1. AWS_BEARER_TOKEN_BEDROCK (recommended)\n"
                "  2. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY\n"
                "See: backend/agent/ghostwriter/OPENHANDS_SDK_BEDROCK_CONFIGURATION.md"
            )

    def load_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Load and format prompt template.

        Args:
            prompt_name: Prompt file name (e.g., "researcher.txt")
            **kwargs: Template variables

        Returns:
            Formatted prompt
        """
        prompts_dir = Path(__file__).parent / "prompts"
        prompt_path = prompts_dir / prompt_name

        with open(prompt_path, "r") as f:
            template = f.read()

        return template.format(**kwargs)

    def load_style_guide(self, style_name: str) -> str:
        """
        Load style guide content.

        Args:
            style_name: Style guide name (technical, academic, conversational, defi_report)

        Returns:
            Style guide content
        """
        style_guides_dir = Path(__file__).parent / "style_guides"
        style_path = style_guides_dir / f"{style_name}.md"

        if not style_path.exists():
            logger.warning(f"Style guide '{style_name}' not found, using 'technical'")
            style_path = style_guides_dir / "technical.md"

        with open(style_path, "r") as f:
            return f.read()

    async def _run_single_researcher(self, topic: str, researcher_id: int) -> str:
        """
        Run a single researcher agent.

        Args:
            topic: Research topic
            researcher_id: ID of this researcher (for file naming)

        Returns:
            Path to created source file
        """
        import asyncio

        # Create Haiku researcher
        researcher_llm = self.create_llm(self.HAIKU)
        researcher = Agent(
            llm=researcher_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        # Create dedicated workspace for this researcher
        researcher_workspace = self.workspace / "00_research"
        researcher_workspace.mkdir(parents=True, exist_ok=True)

        # Create conversation
        conv = Conversation(
            agent=researcher,
            workspace=str(researcher_workspace)
        )

        # Load researcher prompt
        researcher_prompt = self.load_prompt(
            "researcher.txt",
            topic=topic,
            date_accessed=datetime.now().strftime("%Y-%m-%d")
        )

        # Send research message
        message = f"""
{researcher_prompt}

Please save your research findings to a file named "source_{researcher_id}.md" in the current workspace.
"""

        conv.send_message(message)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conv.run)

        source_path = researcher_workspace / f"source_{researcher_id}.md"
        return str(source_path)

    async def run_stage_1_research(self, topic: str) -> Dict[str, Any]:
        """
        Stage 1: Parallel research with Haiku subagents.

        Spawns multiple Haiku research agents in parallel.
        Each agent performs web research and saves findings to source_N.md.

        Args:
            topic: Research topic

        Returns:
            Stage results
        """
        import asyncio

        logger.info(f"[Stage 1/8] Research (parallel Haiku × {self.num_researchers})")

        # Create research directory
        research_dir = self.workspace / "00_research"
        research_dir.mkdir(parents=True, exist_ok=True)

        # Run researchers in parallel
        tasks = [
            self._run_single_researcher(topic, i + 1)
            for i in range(self.num_researchers)
        ]

        source_paths = await asyncio.gather(*tasks)

        # Check how many sources were created
        sources = list(research_dir.glob("source_*.md"))

        logger.info(f"Research complete: {len(sources)} sources gathered")

        return {
            "stage": "research",
            "num_sources": len(sources),
            "sources": [str(s.name) for s in sources]
        }

    async def run_stage_2_draft(self) -> Dict[str, Any]:
        """
        Stage 2: Synthesize research into coherent draft with Sonnet.

        Reads all research sources and creates initial draft with citations.

        Returns:
            Stage results
        """
        logger.info("[Stage 2/8] Draft (Sonnet synthesis)")

        # Drafter agent (Sonnet for quality writing)
        drafter_llm = self.create_llm(self.SONNET)
        drafter = Agent(
            llm=drafter_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(
            agent=drafter,
            workspace=str(self.workspace)
        )

        # Read research sources
        research_dir = self.workspace / "00_research"
        sources = sorted(research_dir.glob("source_*.md"))
        research_sources = "\n\n".join([
            f"--- {s.name} ---\n{s.read_text()}"
            for s in sources
        ])

        drafter_prompt = self.load_prompt(
            "drafter.txt",
            research_sources=research_sources
        )

        conv.send_message(drafter_prompt)
        conv.run()

        draft_path = self.workspace / "01_draft" / "initial_draft.md"

        logger.info(f"Draft complete: {draft_path}")

        return {
            "stage": "draft",
            "draft_path": str(draft_path)
        }

    async def run_stage_3_extract(self) -> Dict[str, Any]:
        """
        Stage 3: Extract atomic claims with Haiku.

        Extracts all factual claims and citations from the draft.

        Returns:
            Stage results
        """
        logger.info("[Stage 3/8] Extract claims (Haiku)")

        # Extractor agent (Haiku for structured extraction)
        extractor_llm = self.create_llm(self.HAIKU)
        extractor = Agent(
            llm=extractor_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(
            agent=extractor,
            workspace=str(self.workspace)
        )

        extractor_prompt = self.load_prompt("extractor.txt")

        conv.send_message(extractor_prompt)
        conv.run()

        claims_path = self.workspace / "02_extraction" / "atomic_claims.json"
        citations_path = self.workspace / "02_extraction" / "citations.json"

        # Load and count claims
        with open(claims_path) as f:
            claims_data = json.load(f)
            num_claims = len(claims_data.get("claims", []))

        logger.info(f"Extraction complete: {num_claims} claims extracted")

        return {
            "stage": "extraction",
            "num_claims": num_claims,
            "claims_path": str(claims_path),
            "citations_path": str(citations_path)
        }

    async def run_stage_4_verify(self) -> Dict[str, Any]:
        """
        Stage 4: 3-layer verification with parallel Haiku agents.

        Layer 1: URL check (bash curl)
        Layer 2: Content fetch (WebBrowser)
        Layer 3: Claim verification (Haiku)

        Returns:
            Stage results including verification rate
        """
        logger.info("[Stage 4/8] Verify claims (3-layer parallel Haiku)")

        # Verifier coordinator (Sonnet)
        verifier_coord_llm = self.create_llm(self.SONNET)
        verifier_coord = Agent(
            llm=verifier_coord_llm,
            tools=[
                Tool(name=FileEditorTool.name),
                Tool(name=TerminalTool.name)
            ]
        )

        conv = Conversation(
            agent=verifier_coord,
            workspace=str(self.workspace)
        )

        verifier_prompt = self.load_prompt("verifier.txt")

        coordinator_message = f"""
Verify all claims in 02_extraction/atomic_claims.json using 3-layer verification:

1. Layer 1: URL Check - Use TerminalTool to run curl -I for each citation URL
   Save results to 03_verification/url_checks.json

2. Layer 2: Content Fetch - Use WebBrowserTool to fetch source content
   Save fetched content to 03_verification/content_fetched/

3. Layer 3: Claim Verification - Use DelegateTool to spawn parallel Haiku verifiers
   Each verifier uses this prompt:
   {verifier_prompt}

Aggregate all results to 03_verification/verification_report.json with:
- total_claims: int
- verified_claims: int
- verification_rate: float (0.0-1.0)
- threshold_met: bool (>= {self.verification_threshold})
- results: list of verification results
"""

        conv.send_message(coordinator_message)
        conv.run()

        # Load verification report
        report_path = self.workspace / "03_verification" / "verification_report.json"
        with open(report_path) as f:
            report = json.load(f)

        verification_rate = report.get("verification_rate", 0.0)
        threshold_met = report.get("threshold_met", False)

        logger.info(
            f"Verification complete: {verification_rate:.1%} "
            f"({report['verified_claims']}/{report['total_claims']} claims)"
        )

        return {
            "stage": "verification",
            "verification_rate": verification_rate,
            "threshold_met": threshold_met,
            "report": report
        }

    async def run_stage_5_critique(self) -> Dict[str, Any]:
        """
        Stage 5: Quality critique with Sonnet.

        Analyzes draft quality and creates revision strategy.

        Returns:
            Stage results
        """
        logger.info("[Stage 5/8] Critique (Sonnet analysis)")

        # Critic agent (Sonnet)
        critic_llm = self.create_llm(self.SONNET)
        critic = Agent(llm=critic_llm, tools=[Tool(name=FileEditorTool.name)])

        conv = Conversation(
            agent=critic,
            workspace=str(self.workspace)
        )

        critic_prompt = self.load_prompt("critic.txt")

        conv.send_message(critic_prompt)
        conv.run()

        critique_path = self.workspace / "04_critique" / "critique.md"

        logger.info(f"Critique complete: {critique_path}")

        return {
            "stage": "critique",
            "critique_path": str(critique_path)
        }

    async def run_stage_6_revise(self) -> Dict[str, Any]:
        """
        Stage 6: Revise unsupported claims with Sonnet + WebSearch.

        Fixes unsupported claims by finding better sources or rewriting.

        Returns:
            Stage results
        """
        logger.info("[Stage 6/8] Revise (Sonnet + WebSearch)")

        # Reviser agent (Sonnet with web access)
        reviser_llm = self.create_llm(self.SONNET)
        reviser = Agent(
            llm=reviser_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(
            agent=reviser,
            workspace=str(self.workspace)
        )

        reviser_prompt = self.load_prompt("reviser.txt")

        conv.send_message(reviser_prompt)
        conv.run()

        revised_draft_path = self.workspace / "05_revision" / "revised_draft.md"

        logger.info(f"Revision complete: {revised_draft_path}")

        return {
            "stage": "revision",
            "revised_draft_path": str(revised_draft_path)
        }

    async def run_stage_7_reverify(self) -> Dict[str, Any]:
        """
        Stage 7: Re-verify revised claims.

        Same as Stage 4 but on revised draft.

        Returns:
            Stage results including updated verification rate
        """
        logger.info("[Stage 7/8] Re-verify (Haiku)")

        # Similar to Stage 4 but working on revised draft
        # For now, delegate to same verification logic
        # TODO: Implement re-verification targeting only changed claims

        return await self.run_stage_4_verify()

    async def run_stage_8_style(self, style_guide: str = "technical") -> Dict[str, Any]:
        """
        Stage 8: Apply style guide with Sonnet.

        Transforms draft to match specified style guide while preserving facts.

        Args:
            style_guide: Style guide name (technical, academic, conversational, defi_report)

        Returns:
            Stage results
        """
        logger.info(f"[Stage 8/8] Style ({style_guide})")

        # Style agent (Sonnet)
        stylist_llm = self.create_llm(self.SONNET)
        stylist = Agent(llm=stylist_llm, tools=[Tool(name=FileEditorTool.name)])

        conv = Conversation(
            agent=stylist,
            workspace=str(self.workspace)
        )

        # Load style guide
        style_guide_content = self.load_style_guide(style_guide)

        # Load revised draft
        revised_draft_path = self.workspace / "05_revision" / "revised_draft.md"
        revised_draft = revised_draft_path.read_text()

        stylist_prompt = self.load_prompt(
            "style_applicator.txt",
            style_guide=style_guide_content,
            draft=revised_draft
        )

        conv.send_message(stylist_prompt)
        conv.run()

        final_report_path = self.workspace / "07_style" / "final_report.md"

        logger.info(f"Styling complete: {final_report_path}")

        return {
            "stage": "style",
            "style_guide": style_guide,
            "final_report_path": str(final_report_path)
        }

    async def run_full_pipeline(
        self,
        topic: str,
        style_guide: str = "technical"
    ) -> Dict[str, Any]:
        """
        Run complete 8-stage pipeline.

        Args:
            topic: Research topic
            style_guide: Style guide to apply (technical, academic, conversational, defi_report)

        Returns:
            Complete results including final report path and metrics
        """
        logger.info(f"=" * 80)
        logger.info(f"Starting Ghostwriter pipeline")
        logger.info(f"Topic: {topic}")
        logger.info(f"Style: {style_guide}")
        logger.info(f"=" * 80)

        # Create session
        self.create_session(topic)

        results = {
            "session_id": self.session_id,
            "topic": topic,
            "style_guide": style_guide,
            "stages": {}
        }

        try:
            # Stage 1: Research
            results["stages"]["research"] = await self.run_stage_1_research(topic)

            # Stage 2: Draft
            results["stages"]["draft"] = await self.run_stage_2_draft()

            # Stage 3: Extract
            results["stages"]["extract"] = await self.run_stage_3_extract()

            # Stage 4: Verify
            results["stages"]["verify"] = await self.run_stage_4_verify()

            # Stages 5-7: Quality loop (with iterations)
            for iteration in range(self.max_revision_iterations):
                logger.info(f"\n--- Quality Loop Iteration {iteration + 1} ---\n")

                # Stage 5: Critique
                results["stages"]["critique"] = await self.run_stage_5_critique()

                # Check if threshold met
                verification_rate = results["stages"]["verify"]["verification_rate"]
                if verification_rate >= self.verification_threshold:
                    logger.info(
                        f"✅ Verification threshold met: {verification_rate:.1%} "
                        f">= {self.verification_threshold:.1%}"
                    )
                    break

                # Stage 6: Revise
                results["stages"]["revise"] = await self.run_stage_6_revise()

                # Stage 7: Re-verify
                results["stages"]["reverify"] = await self.run_stage_7_reverify()

                # Update verification rate for next iteration
                verification_rate = results["stages"]["reverify"]["verification_rate"]

                if verification_rate >= self.verification_threshold:
                    logger.info(
                        f"✅ Verification threshold met after revision: "
                        f"{verification_rate:.1%} >= {self.verification_threshold:.1%}"
                    )
                    break

            # Stage 8: Style
            results["stages"]["style"] = await self.run_stage_8_style(style_guide)

            # Final results
            final_report_path = results["stages"]["style"]["final_report_path"]
            final_verification_rate = results["stages"].get("reverify", results["stages"]["verify"])["verification_rate"]

            results["final_report"] = final_report_path
            results["verification_rate"] = final_verification_rate
            results["success"] = True

            logger.info(f"\n" + "=" * 80)
            logger.info(f"✅ Pipeline complete!")
            logger.info(f"Session: {self.session_id}")
            logger.info(f"Final report: {final_report_path}")
            logger.info(f"Verification rate: {final_verification_rate:.1%}")
            logger.info(f"=" * 80)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            results["success"] = False
            results["error"] = str(e)

        # Save final results
        with open(self.workspace / "pipeline_results.json", "w") as f:
            json.dump(results, f, indent=2)

        return results


# Example usage
async def main():
    """Example usage of Ghostwriter pipeline."""
    pipeline = GhostwriterPipeline(
        workspace_root="/workspace/ghostwriter_sessions",
        aws_region="us-east-1",
        num_researchers=5,
        max_revision_iterations=2
    )

    result = await pipeline.run_full_pipeline(
        topic="DeFi yields on Stellar blockchain in 2025",
        style_guide="defi_report"
    )

    print(f"\nSession ID: {result['session_id']}")
    print(f"Final Report: {result.get('final_report', 'N/A')}")
    print(f"Verification Rate: {result.get('verification_rate', 0):.1%}")


if __name__ == "__main__":
    asyncio.run(main())
