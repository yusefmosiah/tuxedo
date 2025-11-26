"""
Base classes and utilities for Ghostwriter tools.

Provides common functionality for all tool nodes:
- Workspace access
- LLM creation
- Prompt loading
- Result formatting
"""

from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json

from backend.utils.path_manager import PersistentPathManager
from openhands.workspace import LocalWorkspace


@dataclass
class ToolResult:
    """
    Standard result format for all Ghostwriter tools.

    Attributes:
        success: Whether tool executed successfully
        output: Human-readable output message
        output_path: Path to primary output file (relative to workspace)
        metadata: Additional structured data
        error: Error message if success=False
    """
    success: bool
    output: str
    output_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GhostwriterToolBase:
    """
    Base class for all Ghostwriter tool nodes.

    Provides common utilities:
    - Workspace access via PersistentPathManager
    - LLM creation with Bedrock configuration
    - Prompt template loading
    - Consistent result formatting
    """

    # Tool metadata (override in subclasses)
    name: str = "base_tool"
    description: str = "Base tool"

    # Model identifiers
    HAIKU = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    SONNET = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region

    def get_workspace(
        self,
        user_id: str,
        session_id: str
    ) -> tuple[Path, LocalWorkspace]:
        """
        Get workspace directory and LocalWorkspace instance.

        Returns:
            (workspace_dir_path, LocalWorkspace)
        """
        workspace_dir = PersistentPathManager.workspace_dir(user_id, session_id)
        workspace = LocalWorkspace(base_dir=str(workspace_dir))
        return workspace_dir, workspace

    def create_llm(self, model: str):
        """
        Create LLM instance with Bedrock configuration.

        Args:
            model: Model ID (HAIKU or SONNET constant)

        Returns:
            Configured LLM instance
        """
        import os
        from openhands.sdk import LLM

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

    def load_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Load and format prompt template.

        Args:
            prompt_name: Prompt file name (e.g., "researcher.txt")
            **kwargs: Template variables

        Returns:
            Formatted prompt string
        """
        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompt_path = prompts_dir / prompt_name

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")

        with open(prompt_path, "r") as f:
            template = f.read()

        return template.format(**kwargs)

    def ensure_output_dir(self, workspace_dir: Path, dir_name: str):
        """Ensure output directory exists."""
        output_dir = workspace_dir / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def verify_output(
        self,
        workspace_dir: Path,
        output_path: str
    ) -> tuple[bool, Optional[str]]:
        """
        Verify tool output file was created.

        Returns:
            (success, error_message)
        """
        full_path = workspace_dir / output_path
        if not full_path.exists():
            return False, f"Output file not created: {output_path}"

        # Check file is not empty
        if full_path.stat().st_size == 0:
            return False, f"Output file is empty: {output_path}"

        return True, None
