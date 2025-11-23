"""
Test Ghostwriter Tool Integration
"""

import unittest
import asyncio
from unittest.mock import MagicMock, patch
from agent.ghostwriter.tool import ghostwriter_research, _run_ghostwriter_async
from agent.tool_factory import create_user_tools
from agent.context import AgentContext

class TestGhostwriterTool(unittest.IsolatedAsyncioTestCase):
    """Test Ghostwriter Tool Integration"""

    async def test_ghostwriter_tool_execution(self):
        """Test that the ghostwriter tool can be executed."""

        # Mock the pipeline to avoid actual execution
        with patch('agent.ghostwriter.tool.GhostwriterPipeline') as MockPipeline:
            # Setup mock
            mock_instance = MockPipeline.return_value
            mock_instance.run_full_pipeline = MagicMock(return_value=asyncio.Future())
            mock_instance.run_full_pipeline.return_value.set_result({
                "success": True,
                "session_id": "test_session_123",
                "final_report": "/tmp/test_report.md",
                "verification_rate": 0.95
            })

            # Create dummy report file
            with patch('builtins.open', unittest.mock.mock_open(read_data="Test Report Content")):
                # Execute the async implementation directly
                result = await _run_ghostwriter_async(
                    topic="Test Topic",
                    style_guide="general_report",
                    verification_threshold=0.8,
                    max_iterations=1
                )

                # Verify results
                self.assertTrue(result["success"])
                self.assertEqual(result["session_id"], "test_session_123")
                self.assertIn("Test Report Content", result["report_preview"])

                # Verify pipeline was called correctly
                MockPipeline.assert_called_once()
                mock_instance.run_full_pipeline.assert_called_once_with(
                    topic="Test Topic",
                    style_guide="general_report"
                )

    def test_tool_factory_registration(self):
        """Test that the tool is registered in the factory."""

        # Create dummy context
        context = AgentContext(
            user_id="test_user",
            wallet_address="GABC123",
            wallet_mode="external"
        )

        # Get tools
        tools = create_user_tools(context)

        # Check if ghostwriter tool is present
        tool_names = [t.name for t in tools]
        self.assertIn("ghostwriter_tool_wrapper", tool_names)

if __name__ == '__main__':
    unittest.main()
