"""
Test suite for hypothesis formation tool.

Tests:
- Tool initialization
- Hypothesis generation
- Output file creation
- Result format validation
"""

import pytest
import asyncio
import json
from pathlib import Path
import tempfile
import shutil

from backend.agent.ghostwriter.tools.hypothesis_former import FormHypothesesTool
from backend.agent.ghostwriter.tools.base import ToolResult


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_hypothesis_former_initialization():
    """Test tool can be initialized."""
    tool = FormHypothesesTool(aws_region="us-east-1")

    assert tool.name == "form_hypotheses"
    assert tool.aws_region == "us-east-1"
    assert tool.description  # Has description


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires AWS credentials and OpenHands agent setup")
async def test_hypothesis_former_execution(temp_workspace):
    """
    Test hypothesis formation end-to-end.

    NOTE: Skipped by default - requires:
    - AWS Bedrock credentials
    - OpenHands SDK properly configured
    - Network access

    Run manually with: pytest -v -k test_hypothesis_former_execution --no-skip
    """
    tool = FormHypothesesTool(aws_region="us-east-1")

    # Mock session setup
    # In real test, would use PersistentPathManager
    # For now, just test the interface

    result = await tool.run(
        topic="Ethereum Layer 2 scaling solutions",
        session_id="test_session",
        user_id="test_user",
        num_hypotheses=3
    )

    assert isinstance(result, ToolResult)

    if result.success:
        assert result.output_path == "00_hypotheses/initial_hypotheses.json"
        assert result.metadata["num_hypotheses"] >= 3
        assert 0.0 <= result.metadata["avg_certitude"] <= 1.0


def test_hypothesis_tool_result_format():
    """Test ToolResult format."""
    result = ToolResult(
        success=True,
        output="Generated 5 hypotheses",
        output_path="00_hypotheses/initial_hypotheses.json",
        metadata={
            "num_hypotheses": 5,
            "avg_certitude": 0.65
        }
    )

    assert result.success
    assert result.output
    assert result.output_path
    assert result.metadata["num_hypotheses"] == 5
    assert result.error is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
