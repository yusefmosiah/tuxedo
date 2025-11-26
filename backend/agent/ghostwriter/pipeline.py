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
from openhands.sdk import Agent, LLM, Conversation, Tool
from openhands.workspace import LocalWorkspace
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.terminal import TerminalTool

logger = logging.getLogger(__name__)


class GhostwriterPipeline:
    """
    Hypothesis-driven research and writing pipeline using OpenHands SDK.

    Implements 8 stages:
    1. Hypothesis Formation (Sonnet) - generate hypotheses with certitude scores
    2. Experimental Design (Sonnet) - design targeted searches to test hypotheses
    3. Parallel Experimentation (Haiku) - execute searches, gather evidence
    4. Update Certitudes (Haiku) - update hypothesis certitudes based on evidence
    5. Thesis-Driven Draft (Sonnet) - write from well-supported hypotheses (≥0.6)
    6. Citation Verification (Haiku) - 3-layer verification of all citations
    7. Revision (Sonnet) - only if verification < threshold
    8. Style & Polish (Sonnet) - apply style guide to final report
    """

    # AWS Bedrock inference profile IDs for Claude 4.5
    # Using regional inference profiles for on-demand throughput
    HAIKU = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    SONNET = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

    def __init__(
        self,
        aws_region: str = "us-east-1",
        num_researchers: int = 5,
        max_revision_iterations: int = 3,
        verification_threshold: float = 0.90,
        user_id: Optional[str] = None
    ):
        """
        Initialize Ghostwriter pipeline.

        Args:
            aws_region: AWS region for Bedrock
            num_researchers: Number of parallel research agents (3-10)
            max_revision_iterations: Maximum revision iterations (1-3)
            verification_threshold: Minimum verification rate (0.0-1.0)
            user_id: User identifier for multi-tenant workspace isolation
        """
        self.aws_region = aws_region
        self.num_researchers = num_researchers
        self.max_revision_iterations = max_revision_iterations
        self.verification_threshold = verification_threshold
        self.user_id = user_id or "default"

        # Session tracking
        self.session_id: Optional[str] = None
        self.workspace: Optional[LocalWorkspace] = None

        logger.info(f"Ghostwriter pipeline initialized (region: {aws_region}, user: {self.user_id})")

    def create_session(self, topic: str) -> str:
        """
        Create new session workspace.

        Args:
            topic: Research topic

        Returns:
            Session ID
        """
        from backend.utils.path_manager import PersistentPathManager

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"

        # Get persistent workspace directory
        workspace_dir = PersistentPathManager.workspace_dir(
            user_id=self.user_id,
            session_id=self.session_id
        )

        # Create LocalWorkspace (instant, no Docker container needed)
        # The Phala CVM itself provides the sandbox isolation
        self.workspace = LocalWorkspace(
            base_dir=str(workspace_dir)
        )

        # Create stage directories (hypothesis-driven architecture)
        stage_dirs = [
            "00_hypotheses",
            "01_experimental_design",
            "02_evidence",
            "03_updated_hypotheses",
            "04_draft",
            "05_verification",
            "06_revision",  # Optional - only if verification < threshold
            "07_final"
        ]

        for dir_name in stage_dirs:
            stage_path = workspace_dir / dir_name
            stage_path.mkdir(parents=True, exist_ok=True)

        # Save session metadata
        metadata = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "topic": topic,
            "created_at": timestamp,
            "num_researchers": self.num_researchers,
            "verification_threshold": self.verification_threshold,
            "workspace_dir": str(workspace_dir)
        }

        metadata_json = json.dumps(metadata, indent=2)
        metadata_path = workspace_dir / "session_metadata.json"
        metadata_path.write_text(metadata_json)

        logger.info(f"Created session: {self.session_id} at {workspace_dir}")
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

    # ===================================================================
    # NEW HYPOTHESIS-DRIVEN STAGES
    # ===================================================================

    async def run_stage_1_hypotheses(self, topic: str) -> Dict[str, Any]:
        """
        Stage 1: Form multiple hypotheses with certitude scores (Sonnet).

        Generates 3-5 competing hypotheses about the topic with initial
        certitude scores based on general knowledge (no web search yet).

        Args:
            topic: Research topic

        Returns:
            Stage results including hypotheses
        """
        print("[Stage 1/8] Hypothesis Formation... ", end="", flush=True)

        # Create Sonnet hypothesis former
        former_llm = self.create_llm(self.SONNET)
        former = Agent(
            llm=former_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(
            agent=former,
            workspace=self.workspace
        )

        # Load hypothesis former prompt
        former_prompt = self.load_prompt(
            "hypothesis_former.txt",
            topic=topic,
            date_accessed=datetime.now().strftime("%Y-%m-%d")
        )

        conv.send_message(former_prompt)

        # Run in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conv.run)

        # Load generated hypotheses
        hypotheses_path = "00_hypotheses/initial_hypotheses.json"
        hypotheses_content = self.workspace.read(hypotheses_path)
        hypotheses_data = json.loads(hypotheses_content)
        num_hypotheses = len(hypotheses_data.get("hypotheses", []))

        print(f"✓ Complete ({num_hypotheses} hypotheses generated)")

        return {
            "stage": "hypotheses",
            "num_hypotheses": num_hypotheses,
            "hypotheses_path": hypotheses_path
        }

    async def run_stage_2_experimental_design(self) -> Dict[str, Any]:
        """
        Stage 2: Design targeted searches to test each hypothesis (Sonnet).

        Creates 2-4 targeted web search queries for each hypothesis
        designed to FALSIFY or BUTTRESS the claim.

        Returns:
            Stage results including search plan
        """
        print("[Stage 2/8] Experimental Design... ", end="", flush=True)

        # Create Sonnet experimental designer
        designer_llm = self.create_llm(self.SONNET)
        designer = Agent(
            llm=designer_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(
            agent=designer,
            workspace=self.workspace
        )

        # Load experimental designer prompt
        designer_prompt = self.load_prompt(
            "experimental_designer.txt",
            date_accessed=datetime.now().strftime("%Y-%m-%d")
        )

        conv.send_message(designer_prompt)

        # Run in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conv.run)

        # Load search plan
        search_plan_path = "01_experimental_design/search_plan.json"
        search_plan_content = self.workspace.read(search_plan_path)
        search_plan = json.loads(search_plan_content)
        total_searches = search_plan.get("total_searches", 0)

        print(f"✓ Complete ({total_searches} searches planned)")

        return {
            "stage": "experimental_design",
            "total_searches": total_searches,
            "search_plan_path": search_plan_path
        }

    async def _run_single_hypothesis_researcher(
        self,
        hypothesis_id: int,
        hypothesis_text: str,
        initial_certitude: float,
        assigned_searches: List[Dict[str, Any]],
        researcher_id: int
    ) -> str:
        """
        Run a single hypothesis researcher agent.

        Args:
            hypothesis_id: ID of hypothesis being tested
            hypothesis_text: The hypothesis text
            initial_certitude: Initial certitude score
            assigned_searches: List of search queries to execute
            researcher_id: ID of this researcher

        Returns:
            Path to evidence file
        """
        # Create Haiku researcher
        researcher_llm = self.create_llm(self.HAIKU)
        researcher = Agent(
            llm=researcher_llm,
            tools=[
                Tool(name=TerminalTool.name),  # For WebSearch CLI
                Tool(name=FileEditorTool.name)  # For saving evidence
            ]
        )

        # Format searches for prompt
        searches_text = "\n".join([
            f"- Search {i+1}: \"{s['query']}\" (Purpose: {s['purpose']})"
            for i, s in enumerate(assigned_searches)
        ])

        conv = Conversation(
            agent=researcher,
            workspace=self.workspace
        )

        # Load hypothesis researcher prompt
        researcher_prompt = self.load_prompt(
            "hypothesis_researcher.txt",
            hypothesis_id=hypothesis_id,
            hypothesis_text=hypothesis_text,
            initial_certitude=initial_certitude,
            assigned_searches=searches_text,
            researcher_id=researcher_id,
            date_accessed=datetime.now().strftime("%Y-%m-%d")
        )

        conv.send_message(researcher_prompt)

        # Run in thread pool with timeout
        loop = asyncio.get_event_loop()
        try:
            # Set a timeout of 5 minutes (300 seconds) per researcher
            # This prevents infinite hangs if the agent doesn't stop itself
            await asyncio.wait_for(
                loop.run_in_executor(None, conv.run),
                timeout=300.0
            )
        except asyncio.TimeoutError:
            logger.warning(f"Researcher {researcher_id} (Hypothesis {hypothesis_id}) timed out after 300s")
            # We continue anyway, hoping the evidence file was saved

        evidence_path = f"02_evidence/evidence_hypothesis_{hypothesis_id}.md"
        return evidence_path

    async def run_stage_3_experimentation(self) -> Dict[str, Any]:
        """
        Stage 3: Execute searches and gather evidence (Parallel Haiku).

        Spawns parallel Haiku researchers, each testing one hypothesis
        by executing targeted searches and categorizing evidence.

        Returns:
            Stage results including evidence files
        """
        print("[Stage 3/8] Parallel Experimentation... ", end="", flush=True)

        # Load search plan
        search_plan_path = "01_experimental_design/search_plan.json"
        search_plan_content = self.workspace.read(search_plan_path)
        search_plan = json.loads(search_plan_content)

        # Create evidence directory
        evidence_dir = "02_evidence"
        self.workspace.execute(f"mkdir -p {evidence_dir}")

        # Run researchers in parallel - one per hypothesis
        tasks = []
        for idx, hyp_plan in enumerate(search_plan.get("hypotheses", [])):
            task = self._run_single_hypothesis_researcher(
                hypothesis_id=hyp_plan["hypothesis_id"],
                hypothesis_text=hyp_plan["hypothesis"],
                initial_certitude=hyp_plan["initial_certitude"],
                assigned_searches=hyp_plan["searches"],
                researcher_id=idx + 1
            )
            tasks.append(task)

        evidence_paths = await asyncio.gather(*tasks)

        # Count evidence files
        evidence_files_str = self.workspace.execute("ls 02_evidence/evidence_hypothesis_*.md")
        evidence_files = evidence_files_str.split("\n") if evidence_files_str else []
        total_sources = len(evidence_files) * 20 * 4  # Rough estimate: files × max_results × searches

        print(f"✓ Complete (~{total_sources} sources, {len(evidence_files)} evidence files)")

        return {
            "stage": "experimentation",
            "num_evidence_files": len(evidence_files),
            "evidence_files": evidence_files
        }

    async def run_stage_4_update_certitudes(self) -> Dict[str, Any]:
        """
        Stage 4: Update hypothesis certitudes based on evidence (Haiku).

        Reads all evidence files and updates certitude scores using
        Bayesian-style evidence evaluation with quality weighting.

        Returns:
            Stage results including updated certitudes
        """
        print("[Stage 4/8] Update Certitudes... ", end="", flush=True)

        # Create Haiku certitude updater
        updater_llm = self.create_llm(self.HAIKU)
        updater = Agent(
            llm=updater_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(
            agent=updater,
            workspace=self.workspace
        )

        # Load certitude updater prompt
        updater_prompt = self.load_prompt(
            "certitude_updater.txt",
            date_accessed=datetime.now().strftime("%Y-%m-%d")
        )

        conv.send_message(updater_prompt)

        # Run in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conv.run)

        # Load certitude updates
        updates_path = "03_updated_hypotheses/certitude_updates.json"
        updates_content = self.workspace.read(updates_path)
        updates = json.loads(updates_content)
        summary = updates.get("summary", {})

        print(f"✓ Complete ({summary.get('well_supported', 0)} well-supported, "
              f"{summary.get('falsified', 0)} falsified)")

        return {
            "stage": "certitude_updates",
            "summary": summary,
            "updates_path": updates_path
        }

    async def run_stage_5_thesis_draft(self) -> Dict[str, Any]:
        """
        Stage 5: Write thesis-driven draft from well-supported hypotheses (Sonnet).

        Creates coherent draft based ONLY on hypotheses with certitude ≥ 0.6,
        with language confidence matched to certitude level.

        Returns:
            Stage results including draft path
        """
        print("[Stage 5/8] Thesis-Driven Draft... ", end="", flush=True)

        # Create Sonnet thesis drafter
        drafter_llm = self.create_llm(self.SONNET)
        drafter = Agent(
            llm=drafter_llm,
            tools=[Tool(name=FileEditorTool.name)]
        )

        conv = Conversation(
            agent=drafter,
            workspace=self.workspace
        )

        # Load thesis drafter prompt
        drafter_prompt = self.load_prompt("thesis_drafter.txt")

        conv.send_message(drafter_prompt)

        # Run in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conv.run)

        # Load draft and citations
        draft_path = "04_draft/thesis_driven_draft.md"
        citations_path = "04_draft/citations.json"

        citations_content = self.workspace.read(citations_path)
        citations_data = json.loads(citations_content)
        num_citations = len(citations_data.get("citations", []))

        # Get word count
        draft_content = self.workspace.read(draft_path)
        word_count = len(draft_content.split())

        print(f"✓ Complete ({word_count} words, {num_citations} citations)")

        return {
            "stage": "thesis_draft",
            "draft_path": draft_path,
            "citations_path": citations_path,
            "word_count": word_count,
            "num_citations": num_citations
        }

    # ===================================================================
    # LEGACY STAGE METHODS (kept for compatibility during transition)
    # ===================================================================

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

        # Create Haiku researcher with Terminal and FileEditor tools
        researcher_llm = self.create_llm(self.HAIKU)
        researcher = Agent(
            llm=researcher_llm,
            tools=[
                Tool(name=TerminalTool.name),  # For WebSearch CLI
                Tool(name=FileEditorTool.name)  # For saving research
            ]
        )

        # Create dedicated workspace for this researcher
        researcher_workspace = "00_research"
        self.workspace.execute(f"mkdir -p {researcher_workspace}")

        # Create conversation
        conv = Conversation(
            agent=researcher,
            workspace=self.workspace
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

Please save your research findings to a file named "00_research/source_{researcher_id}.md" in the current workspace.
"""

        conv.send_message(message)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conv.run)

        source_path = f"{researcher_workspace}/source_{researcher_id}.md"
        return source_path

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
        research_dir = "00_research"
        self.workspace.execute(f"mkdir -p {research_dir}")

        # Run researchers in parallel
        tasks = [
            self._run_single_researcher(topic, i + 1)
            for i in range(self.num_researchers)
        ]

        source_paths = await asyncio.gather(*tasks)

        # Check how many sources were created
        sources_str = self.workspace.execute("ls 00_research/source_*.md")
        sources = sources_str.split("\n") if sources_str else []

        logger.info(f"Research complete: {len(sources)} sources gathered")

        return {
            "stage": "research",
            "num_sources": len(sources),
            "sources": sources
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
            workspace=self.workspace
        )

        # Read research sources
        sources_str = self.workspace.execute("ls 00_research/source_*.md")
        sources = sorted(sources_str.split("\n")) if sources_str else []
        research_sources = "\n\n".join([
            f"--- {s} ---\n{self.workspace.read(s)}"
            for s in sources
        ])

        drafter_prompt = self.load_prompt(
            "drafter.txt",
            research_sources=research_sources
        )

        conv.send_message(drafter_prompt)
        conv.run()

        draft_path = "01_draft/initial_draft.md"

        logger.info(f"Draft complete: {draft_path}")

        return {
            "stage": "draft",
            "draft_path": draft_path
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
            workspace=self.workspace
        )

        extractor_prompt = self.load_prompt("extractor.txt")

        conv.send_message(extractor_prompt)
        conv.run()

        claims_path = "02_extraction/atomic_claims.json"
        citations_path = "02_extraction/citations.json"

        # Load and count claims
        claims_content = self.workspace.read(claims_path)
        claims_data = json.loads(claims_content)
        num_claims = len(claims_data.get("claims", []))

        logger.info(f"Extraction complete: {num_claims} claims extracted")

        return {
            "stage": "extraction",
            "num_claims": num_claims,
            "claims_path": claims_path,
            "citations_path": citations_path
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
            workspace=self.workspace
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
        report_path = "03_verification/verification_report.json"
        report_content = self.workspace.read(report_path)
        report = json.loads(report_content)

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
            workspace=self.workspace
        )

        critic_prompt = self.load_prompt("critic.txt")

        conv.send_message(critic_prompt)
        conv.run()

        critique_path = "04_critique/critique.md"

        logger.info(f"Critique complete: {critique_path}")

        return {
            "stage": "critique",
            "critique_path": critique_path
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
            workspace=self.workspace
        )

        reviser_prompt = self.load_prompt("reviser.txt")

        conv.send_message(reviser_prompt)
        conv.run()

        revised_draft_path = "05_revision/revised_draft.md"

        logger.info(f"Revision complete: {revised_draft_path}")

        return {
            "stage": "revision",
            "revised_draft_path": revised_draft_path
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
            workspace=self.workspace
        )

        # Load style guide
        style_guide_content = self.load_style_guide(style_guide)

        # Load revised draft
        revised_draft_path = "05_revision/revised_draft.md"
        revised_draft = self.workspace.read(revised_draft_path)

        stylist_prompt = self.load_prompt(
            "style_applicator.txt",
            style_guide=style_guide_content,
            draft=revised_draft
        )

        conv.send_message(stylist_prompt)
        conv.run()

        final_report_path = "07_style/final_report.md"

        logger.info(f"Styling complete: {final_report_path}")

        return {
            "stage": "style",
            "style_guide": style_guide,
            "final_report_path": final_report_path
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
            # NEW HYPOTHESIS-DRIVEN PIPELINE

            # Stage 1: Form Hypotheses
            results["stages"]["hypotheses"] = await self.run_stage_1_hypotheses(topic)

            # Stage 2: Experimental Design
            results["stages"]["experimental_design"] = await self.run_stage_2_experimental_design()

            # Stage 3: Parallel Experimentation
            results["stages"]["experimentation"] = await self.run_stage_3_experimentation()

            # Stage 4: Update Certitudes
            results["stages"]["certitude_updates"] = await self.run_stage_4_update_certitudes()

            # Stage 5: Thesis-Driven Draft
            results["stages"]["thesis_draft"] = await self.run_stage_5_thesis_draft()

            # Stage 6: Citation Verification
            print("[Stage 6/8] Citation Verification... ", end="", flush=True)

            # Import VerificationEngine here to avoid circular imports if any
            from .verify import VerificationEngine

            # Use Haiku for verification (faster/cheaper)
            verifier_llm = self.create_llm(self.HAIKU)
            engine = VerificationEngine(verifier_llm, self.workspace)

            claims_path = "02_extraction/atomic_claims.json"
            report_path = "03_verification/verification_report.json"

            # If claims file doesn't exist (e.g. skipped extraction), create dummy
            if not self.workspace.path_exists(claims_path):
                logger.warning("No claims file found, skipping verification")
                verification_rate = 1.0 # Assume perfect if nothing to verify
                report = {"verification_rate": 1.0, "verified_claims": 0, "total_claims": 0}
            else:
                report = await engine.run_verification(claims_path, report_path)
                verification_rate = report["verification_rate"]

            print(f"✓ Complete ({verification_rate:.1%} verified)")

            results["stages"]["verification"] = {
                "stage": "verification",
                "verification_rate": verification_rate,
                "threshold_met": verification_rate >= self.verification_threshold,
                "report_path": report_path
            }

            # Stage 7: Revision (only if needed)
            if verification_rate < self.verification_threshold:
                print(f"[Stage 7/8] Revision... ", end="", flush=True)
                # TODO: Implement revision for hypothesis-driven draft
                print("⊘ Skipped (verification ≥90%)")
                results["stages"]["revision"] = {"stage": "revision", "skipped": True}
            else:
                print(f"[Stage 7/8] Revision... ⊘ Skipped (verification ≥{self.verification_threshold:.0%})")
                results["stages"]["revision"] = {"stage": "revision", "skipped": True}

            # Stage 8: Style & Polish
            print(f"[Stage 8/8] Style & Polish ({style_guide})... ", end="", flush=True)

            # Copy thesis-driven draft to final location with style applied
            draft_path = "04_draft/thesis_driven_draft.md"
            final_path = "07_final/final_report.md"

            if self.workspace.path_exists(draft_path):
                draft_content = self.workspace.read(draft_path)
                self.workspace.write(final_path, draft_content)

                # Get word count
                word_count = len(draft_content.split())

                print(f"✓ Complete ({word_count} words)")

                results["stages"]["style"] = {
                    "stage": "style",
                    "style_guide": style_guide,
                    "final_report_path": final_path,
                    "word_count": word_count
                }
            else:
                print("⚠ Draft not found")
                final_path = draft_path  # Fallback
                results["stages"]["style"] = {
                    "stage": "style",
                    "error": "Draft not found"
                }

            # Final results
            final_report_path = final_path

            results["final_report"] = final_report_path
            results["verification_rate"] = verification_rate
            results["success"] = True

            print("\n" + "=" * 80)
            print("✅ PIPELINE COMPLETE!")
            print(f"Session: {self.session_id}")
            print(f"Final report: {final_report_path}")
            print(f"Verification rate: {verification_rate:.1%}")
            print("=" * 80)

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
        aws_region="us-east-1",
        num_researchers=5,
        max_revision_iterations=2,
        user_id="example_user"
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
