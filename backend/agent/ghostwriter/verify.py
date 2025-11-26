"""
Citation Verification Module for Ghostwriter.

Implements 3-layer verification:
1. URL Accessibility Check (aiohttp)
2. Content Fetching & Extraction (aiohttp + BeautifulSoup)
3. Claim Verification (LLM)
"""

import os
import json
import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from pathlib import Path

from openhands.sdk import Agent, LLM, Conversation, Tool, LocalWorkspace
from openhands.tools.file_editor import FileEditorTool

logger = logging.getLogger(__name__)

class VerificationEngine:
    """
    Engine for verifying claims against their citations.
    """

    def __init__(self, llm: LLM, workspace_dir: Path):
        """
        Initialize VerificationEngine.

        Args:
            llm: Configured LLM instance (should be Haiku for speed/cost)
            workspace_dir: Directory for saving verification artifacts
        """
        self.llm = llm
        self.workspace_dir = workspace_dir
        self.verify_dir = workspace_dir / "03_verification"
        self.content_dir = self.verify_dir / "content_fetched"

        # Ensure directories exist
        self.verify_dir.mkdir(parents=True, exist_ok=True)
        self.content_dir.mkdir(parents=True, exist_ok=True)

    async def check_url(self, url: str) -> Dict[str, Any]:
        """
        Layer 1: Check if URL is accessible.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, allow_redirects=True, timeout=10) as response:
                    return {
                        "accessible": 200 <= response.status < 400,
                        "status_code": response.status,
                        "url": url
                    }
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e),
                "url": url
            }

    async def fetch_content(self, url: str) -> str:
        """
        Layer 2: Fetch content and extract main text.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, allow_redirects=True, timeout=15) as response:
                    if response.status != 200:
                        return ""

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()

                    text = soup.get_text()

                    # Break into lines and remove leading/trailing space on each
                    lines = (line.strip() for line in text.splitlines())
                    # Break multi-headlines into a line each
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    # Drop blank lines
                    text = '\n'.join(chunk for chunk in chunks if chunk)

                    return text[:10000]  # Limit content size
        except Exception as e:
            logger.warning(f"Failed to fetch content from {url}: {e}")
            return ""

    async def verify_claim(self, claim: str, url: str, content: str) -> Dict[str, Any]:
        """
        Layer 3: Verify claim using LLM.
        """
        if not content:
            return {
                "supported": False,
                "confidence": 0.0,
                "reasoning": "Could not fetch content from source"
            }

        # Create a specialized agent for this single verification task
        verifier = Agent(
            llm=self.llm,
            tools=[] # No tools needed, pure context analysis
        )

        ws = LocalWorkspace(self.workspace_dir)
        conv = Conversation(
            agent=verifier,
            workspace=ws,
        )

        prompt = f"""You are a fact-checker verifying a claim against a source.

SOURCE URL: {url}

SOURCE CONTENT (TRUNCATED):
{content[:4000]}

CLAIM TO VERIFY:
"{claim}"

TASK:
Determine if the source content supports the claim.

INSTRUCTIONS:
1. "supported": The source explicitly states the claim or directly implies it.
2. "unsupported": The source does not mention the claim, contradicts it, or is unrelated.
3. Be strict. If the source is 404 or empty, it is unsupported.

Respond with JSON ONLY:
{{
  "supported": boolean,
  "confidence": float (0.0-1.0),
  "reasoning": "brief explanation",
  "quote": "exact quote from text if supported, else null"
}}
"""

        try:
            # We run this synchronously in the thread pool because conv.run is blocking?
            # Actually conv.run is blocking, but we can use run_in_executor
            # However, we want to get the response text.
            # OpenHands Conversation doesn't easily return the last message content directly from run()
            # But we can inspect conv.messages after run.

            # Since we are inside an async function, we should run the blocking agent in an executor
            loop = asyncio.get_event_loop()

            # Send message
            conv.send_message(prompt)

            # Run agent
            await loop.run_in_executor(None, conv.run)

            # Get last message from agent
            # Assuming the last message in conversation is the agent's response
            # We need to find the last message with role 'assistant'
            # Accessing private attribute _history or similar might be needed if no public API
            # Looking at OpenHands SDK usage in pipeline.py, it doesn't show how to get response.
            # But usually conv.messages or similar.
            # Let's assume we can parse the last message.

            # WORKAROUND: Since I don't have the full SDK docs, I'll assume I can read the conversation history
            # or that conv.run() returns something useful? No, pipeline.py ignores return value.
            # pipeline.py uses file artifacts for communication.
            # I should probably ask the agent to write to a file?
            # Or I can try to access conv.history if available.

            # Let's try to make the agent write the JSON to a file.
            output_filename = f"verification_{hash(claim + url)}.json"
            output_path = self.verify_dir / "temp" / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            prompt_with_file = prompt + f"\n\nSave your JSON response to: {output_path}"

            # Re-create conversation with FileEditorTool
            verifier = Agent(
                llm=self.llm,
                tools=[Tool(name=FileEditorTool.name)]
            )
            ws = LocalWorkspace(self.workspace_dir)
            conv = Conversation(
                agent=verifier,
                workspace=ws,
            )
            conv.send_message(prompt_with_file)
            await loop.run_in_executor(None, conv.run)

            if output_path.exists():
                with open(output_path, 'r') as f:
                    result = json.load(f)
                # Cleanup
                os.remove(output_path)
                return result
            else:
                return {
                    "supported": False,
                    "confidence": 0.0,
                    "reasoning": "Agent failed to produce verification file"
                }

        except Exception as e:
            logger.error(f"Error in verify_claim: {e}")
            return {
                "supported": False,
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}"
            }

    async def process_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single claim through all 3 layers.
        """
        claim = claim_data.get("claim")
        url = claim_data.get("url")

        result = {
            "claim": claim,
            "url": url,
            "layers": {
                "url_check": None,
                "content_fetch": None,
                "verification": None
            },
            "verified": False
        }

        if not url:
            result["error"] = "No URL provided"
            return result

        # Layer 1: URL Check
        url_check = await self.check_url(url)
        result["layers"]["url_check"] = url_check

        if not url_check["accessible"]:
            return result

        # Layer 2: Content Fetch
        content = await self.fetch_content(url)
        result["layers"]["content_fetch"] = {
            "success": bool(content),
            "length": len(content)
        }

        # Save content for debugging/audit
        if content:
            safe_filename = "".join(c for c in url if c.isalnum())[:50] + ".txt"
            with open(self.content_dir / safe_filename, "w") as f:
                f.write(content)

        # Layer 3: Verification
        verification = await self.verify_claim(claim, url, content)
        result["layers"]["verification"] = verification
        result["verified"] = verification.get("supported", False)

        return result

    async def run_verification(self, claims_path: Path, output_path: Path) -> Dict[str, Any]:
        """
        Run verification for all claims in the claims file.
        """
        logger.info(f"Starting verification for {claims_path}")

        with open(claims_path, 'r') as f:
            data = json.load(f)
            claims = data.get("claims", [])

        tasks = [self.process_claim(claim) for claim in claims]
        results = await asyncio.gather(*tasks)

        verified_count = sum(1 for r in results if r["verified"])
        total = len(results)
        rate = verified_count / total if total > 0 else 0.0

        report = {
            "total_claims": total,
            "verified_claims": verified_count,
            "verification_rate": rate,
            "results": results
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report
