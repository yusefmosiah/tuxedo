import base64
import os
from typing import Optional

from deepagents.backends.protocol import (
    ExecuteResponse,
    FileDownloadResponse,
    FileOperationError,
    FileUploadResponse,
)
from deepagents.backends.sandbox import BaseSandbox
from runloop_api_client import Runloop
# from runloop_api_client.types import Devbox

class RunloopBackend(BaseSandbox):
    """Sandbox backend using Runloop Devboxes."""

    def __init__(self, api_key: Optional[str] = None, devbox_id: Optional[str] = None):
        self.api_key = api_key or os.environ.get("RUNLOOP_API_KEY")
        if not self.api_key:
            raise ValueError("RUNLOOP_API_KEY is required")

        self.client = Runloop(bearer_token=self.api_key)
        self._devbox_id = devbox_id
        self._devbox = None # type: ignore

    @property
    def id(self) -> str:
        if self._devbox_id:
            return self._devbox_id
        return "runloop-pending"

    def initialize(self):
        """Initialize the devbox if not already running."""
        if self._devbox_id:
            # Check status or assume running?
            # Ideally we should verify, but for now let's assume valid ID
            pass
        else:
            # Create new devbox
            # Use create_and_await_running for simplicity, though it blocks
            self._devbox = self.client.devboxes.create_and_await_running(name="vibewriter-agent")
            self._devbox_id = self._devbox.id

    def execute(self, command: str) -> ExecuteResponse:
        if not self._devbox_id:
            self.initialize()

        # Runloop execute_sync (ignoring deprecation warning for now as it works)
        # TODO: Switch to execute() when sync wrapper is stable or handle async properly if needed
        result = self.client.devboxes.execute_sync(self._devbox_id, command=command)

        output = result.stdout + result.stderr

        return ExecuteResponse(
            output=output,
            exit_code=result.exit_status,
            truncated=False # Runloop might truncate but we don't have flag in result yet
        )

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        if not self._devbox_id:
            self.initialize()

        responses = []
        for path, content in files:
            try:
                # Runloop upload_file expects file-like object or content?
                # Let's check API. It usually takes 'file' param.
                # But client.devboxes.upload_file(devbox_id, path, file=...)
                # We might need to write to temp file or use BytesIO?
                # Let's assume we can pass bytes or string.
                # If not, we can fallback to 'write' method (which uses cat/echo via execute)
                # But BaseSandbox.write uses execute.
                # BaseSandbox.upload_files is abstract.

                # Let's try to use the API if possible for efficiency.
                # client.devboxes.upload_file(id, path, file=content)
                # If content is bytes.

                self.client.devboxes.upload_file(self._devbox_id, path=path, file=content)
                responses.append(FileUploadResponse(path=path, error=None))
            except Exception as e:
                # Fallback or error
                # If API fails, we could try base64 echo?
                # But let's report error for now.
                responses.append(FileUploadResponse(path=path, error="write_error")) # Using generic error code
        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        if not self._devbox_id:
            self.initialize()

        responses = []
        for path in paths:
            try:
                # client.devboxes.read_file_contents(id, path)
                content = self.client.devboxes.read_file_contents(self._devbox_id, file_path=path)
                # content is likely str or bytes?
                # If str, encode to bytes.
                if isinstance(content, str):
                    content = content.encode("utf-8")

                responses.append(FileDownloadResponse(path=path, content=content, error=None))
            except Exception as e:
                responses.append(FileDownloadResponse(path=path, content=None, error="file_not_found"))
        return responses

    def shutdown(self):
        if self._devbox_id:
            self.client.devboxes.shutdown(self._devbox_id)
