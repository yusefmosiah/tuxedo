# backend/openhands_utils.py
from pathlib import Path

def MOCK_default_sdk_project_root() -> Path:
    """
    MOCK - Resolve top-level OpenHands UV workspace root.
    This function is a mock replacement for the original implementation in
    the OpenHands SDK. The original version was tightly coupled to the
    internal monorepo structure of the SDK and would fail when used as a
    library. This mock simply returns the repository root, which is a more
    flexible and common approach.
    """
    return Path("/app")

def apply_openhands_patch():
    """
    Apply monkey-patch to the OpenHands SDK to bypass its strict
    workspace validation.
    """
    try:
        from openhands.agent_server.docker import build
        build._default_sdk_project_root = MOCK_default_sdk_project_root
    except ImportError:
        # This is not critical if the module is not used in a specific context
        pass
