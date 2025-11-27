import sys
import os
import unittest
from unittest.mock import MagicMock

# Add jazzhands to path so we can import 'openhands' and 'choir'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from choir.runtime.factory import RuntimeFactory
from choir.runtime.base import ChoirRuntime
from choir.runtime.runloop import RunLoopChoirRuntime
from choir.runtime.era import EraRuntime

class TestChoirRuntime(unittest.TestCase):
    def test_factory_creates_runloop(self):
        config_mock = MagicMock()
        # Mock specific config attributes accessed in RemoteRuntime.__init__
        config_mock.sandbox.api_key = "test_key"
        config_mock.sandbox.remote_runtime_api_url = "http://test"
        config_mock.sandbox.remote_runtime_class = None
        config_mock.workspace_base = None

        # Mock RemoteRuntimeBuilder since __init__ creates it
        with unittest.mock.patch('openhands.runtime.impl.remote.remote_runtime.RemoteRuntimeBuilder'):
             runtime = RuntimeFactory.create(
                user_id="user123",
                provider="runloop",
                config=config_mock,
                event_stream=MagicMock(),
                llm_registry=MagicMock()
            )

        self.assertIsInstance(runtime, ChoirRuntime)
        self.assertIsInstance(runtime, RunLoopChoirRuntime)
        self.assertEqual(runtime.user_id, "user123")

    def test_factory_creates_era(self):
        runtime = RuntimeFactory.create(user_id="user456", provider="era")

        self.assertIsInstance(runtime, ChoirRuntime)
        self.assertIsInstance(runtime, EraRuntime)
        self.assertEqual(runtime.user_id, "user456")
        self.assertFalse(runtime._connected)

if __name__ == "__main__":
    unittest.main()
