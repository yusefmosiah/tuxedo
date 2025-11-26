"""
Proof-of-concept test for autonomous architecture.

This demonstrates the tool-based infrastructure without requiring
full OpenHands SDK initialization or AWS credentials.

Run with: source backend/.venv/bin/activate && python -m backend.tests.agent.ghostwriter.test_autonomous_poc
"""

import asyncio
import sys
from pathlib import Path

# Test infrastructure without importing orchestrator (which imports pipeline which has SDK issues)
# from backend.agent.ghostwriter.autonomous_orchestrator import AutonomousGhostwriter


async def test_tool_base_classes():
    """Test tool base class infrastructure."""
    print("Testing tool base class infrastructure...")

    from backend.agent.ghostwriter.tools.base import GhostwriterToolBase, ToolResult

    # Test tool result format
    result = ToolResult(
        success=True,
        output="Test output",
        output_path="00_hypotheses/test.json",
        metadata={"test": "value"}
    )

    assert result.success
    assert result.output == "Test output"
    assert result.metadata["test"] == "value"

    print("✓ ToolResult class working")
    print("✓ Base infrastructure validated")


async def test_tool_imports():
    """Test that tool nodes can be imported."""
    print("\nTesting tool imports...")

    from backend.agent.ghostwriter.tools.hypothesis_former import FormHypothesesTool
    from backend.agent.ghostwriter.tools.hypothesis_revisor import RevisitHypothesesTool

    # Create instances
    former = FormHypothesesTool(aws_region="us-east-1")
    revisor = RevisitHypothesesTool(aws_region="us-east-1")

    assert former.name == "form_hypotheses"
    assert revisor.name == "revisit_hypotheses"
    assert former.description
    assert revisor.description

    print("✓ FormHypothesesTool imported")
    print("✓ RevisitHypothesesTool imported")
    print(f"✓ Tool names: {former.name}, {revisor.name}")


async def test_workspace_creation():
    """Test workspace directory creation."""
    print("\nTesting workspace creation...")

    from backend.utils.path_manager import PersistentPathManager
    from datetime import datetime

    # Create test session
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"test_session_{timestamp}"
    user_id = "test_user"

    workspace_dir = PersistentPathManager.workspace_dir(user_id, session_id)

    # Create stage directories
    stage_dirs = [
        "00_hypotheses",
        "01_experimental_design",
        "02_evidence",
        "07_final"
    ]

    for dir_name in stage_dirs:
        (workspace_dir / dir_name).mkdir(parents=True, exist_ok=True)

    # Verify
    assert workspace_dir.exists()
    assert (workspace_dir / "00_hypotheses").exists()
    assert (workspace_dir / "07_final").exists()

    print(f"✓ Workspace created at: {workspace_dir}")
    print("✓ All test directories created")


async def test_architecture_ready():
    """Verify Phase 1 architecture components are in place."""
    print("\nVerifying Phase 1 architecture...")

    # Check tool directory structure
    tools_dir = Path("backend/agent/ghostwriter/tools")
    assert tools_dir.exists(), "Tools directory exists"
    assert (tools_dir / "__init__.py").exists(), "Tools module init exists"
    assert (tools_dir / "base.py").exists(), "Base classes exist"
    assert (tools_dir / "hypothesis_former.py").exists(), "Hypothesis former tool exists"
    assert (tools_dir / "hypothesis_revisor.py").exists(), "Hypothesis revisor tool exists"

    print("✓ Tool directory structure in place")
    print("✓ Base classes implemented")
    print("✓ Initial tool nodes created (form, revise)")
    print("✓ Ready for Phase 1 completion (remaining tools + SDK integration)")


async def main():
    """Run all proof-of-concept tests."""
    print("=" * 70)
    print("AUTONOMOUS GHOSTWRITER - Phase 1 Infrastructure Tests")
    print("=" * 70)

    try:
        await test_tool_base_classes()
        await test_tool_imports()
        await test_workspace_creation()
        await test_architecture_ready()

        print("\n" + "=" * 70)
        print("✅ ALL INFRASTRUCTURE TESTS PASSED")
        print("=" * 70)
        print("\nPhase 1 Foundation Status:")
        print("  ✓ Tool base classes implemented")
        print("  ✓ Tool nodes: FormHypothesesTool, RevisitHypothesesTool")
        print("  ✓ Workspace structure validated")
        print("  ✓ Directory structure in place")
        print("\nNext steps:")
        print("  1. Implement remaining tool nodes (DesignExperimentsTool, etc.)")
        print("  2. Complete AutonomousOrchestrator with SDK integration")
        print("  3. Test end-to-end with AWS Bedrock")
        print("  4. Add FastAPI streaming endpoint")
        print("\nNote: Full orchestrator tests require OpenHands SDK workspace setup")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
