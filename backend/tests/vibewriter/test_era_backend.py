import pytest
from unittest.mock import patch, MagicMock
from backend.vibewriter.sandbox.era_backend import EraBackend
from deepagents.backends.protocol import WriteResult, EditResult

# Test the EraBackend logic without needing actual ERA/VM

@pytest.fixture
def mock_sandbox():
    with patch("backend.vibewriter.sandbox.era_backend.EraSandbox") as MockSandbox:
        instance = MockSandbox.return_value
        yield instance

def test_era_backend_read(mock_sandbox):
    # Setup
    backend = EraBackend(vm_id="test_vm")
    mock_sandbox.read_file.return_value = "line1\nline2\nline3"

    # Execute
    result = backend.read("test.txt")

    # Verify
    mock_sandbox.read_file.assert_called_with("test.txt")
    assert "     1 | line1" in result
    assert "     2 | line2" in result

def test_era_backend_read_not_found(mock_sandbox):
    backend = EraBackend(vm_id="test_vm")
    mock_sandbox.read_file.side_effect = FileNotFoundError("Not found")

    result = backend.read("missing.txt")
    assert "Error: File missing.txt not found." in result

def test_era_backend_write(mock_sandbox):
    backend = EraBackend(vm_id="test_vm")

    result = backend.write("test.txt", "content")

    mock_sandbox.write_file.assert_called_with("test.txt", "content")
    # Check it returns a result object (WriteResult is Pydantic/Dataclass-like)
    assert result.path == "test.txt"
    assert result.error is None

def test_era_backend_ls_info(mock_sandbox):
    backend = EraBackend(vm_id="test_vm")
    # ls -F output mock
    mock_sandbox.execute.return_value = (0, "file1.txt\ndir1/\n", "")

    files = backend.ls_info("/app")

    assert len(files) == 2
    # FileInfo is a TypedDict (dict subclass), so use key access
    assert files[0]['path'].endswith("file1.txt")
    assert not files[0]['is_dir']
    assert files[1]['path'].endswith("dir1")
    assert files[1]['is_dir']
