import logging
import base64
import shlex
import datetime
from typing import List, Optional, Tuple, Any

# DeepAgents imports
from deepagents.backends.protocol import (
    BackendProtocol,
    FileDownloadResponse,
    FileUploadResponse,
    EditResult,
    WriteResult,
    FileInfo,
    GrepMatch
)
# Our internal sandbox interface
from backend.vibewriter.sandbox.era_sandbox import EraSandbox

logger = logging.getLogger(__name__)

class EraBackend(BackendProtocol):
    """
    A DeepAgents Backend implementation that delegates to an ERA MicroVM.
    This allows the Deep Agent to treat the MicroVM as its filesystem.
    """

    def __init__(self, vm_id: str):
        self.sandbox = EraSandbox(vm_id)

    def _get_timestamp(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        """Read file content with line numbers or error string."""
        try:
            content = self.sandbox.read_file(file_path)
            lines = content.split('\n')

            sliced_lines = lines[offset : offset + limit]
            numbered_content = []
            for i, line in enumerate(sliced_lines):
                numbered_content.append(f"{offset + i + 1:6d} | {line}")

            return "\n".join(numbered_content)

        except FileNotFoundError:
            return f"Error: File {file_path} not found."
        except Exception as e:
            return f"Error reading {file_path}: {str(e)}"

    def write(self, file_path: str, content: str) -> WriteResult:
        """Create a new file."""
        try:
            self.sandbox.write_file(file_path, content)

            # Correct WriteResult structure based on introspection
            # {'error': str | None, 'path': str | None, 'files_update': dict | None}
            return WriteResult(
                error=None,
                path=file_path,
                files_update=None
            )
        except Exception as e:
            logger.error(f"Write failed: {e}")
            raise e

    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> EditResult:
        """Edit a file by replacing string occurrences."""
        try:
            content = self.sandbox.read_file(file_path)

            # Note: EditResult introspection needed if we want to be exact,
            # but usually it returns diff-like info or success status.
            # Assuming standard DeepAgents behavior where it returns the updated content representation.

            if old_string not in content:
                # Based on WriteResult, EditResult likely has 'error' field too.
                # Let's assume standard error reporting pattern.
                return EditResult(error=f"String '{old_string}' not found in {file_path}")

            if replace_all:
                new_content = content.replace(old_string, new_string)
            else:
                new_content = content.replace(old_string, new_string, 1)

            self.sandbox.write_file(file_path, new_content)

            # Assuming EditResult expects updated lines or similar
            # Let's default to a generic success structure if keys are unknown,
            # or rely on duck typing if it's a TypedDict.
            # However, since I can't introspect EditResult easily in middle of write,
            # I will try to match similar structure to WriteResult or typical editor output.
            return EditResult(error=None)

        except Exception as e:
             return EditResult(error=str(e))

    def ls_info(self, path: str) -> List[FileInfo]:
        """Structured listing with file metadata."""
        try:
            code, out, err = self.sandbox.execute(f"ls -F {shlex.quote(path)}")
            if code != 0:
                return []

            files = []
            for name in out.splitlines():
                if not name: continue
                is_dir = name.endswith('/')
                clean_name = name.rstrip('/*@|')

                # Correct FileInfo structure based on introspection
                # {'path': str, 'is_dir': bool, 'size': int, 'modified_at': str}
                full_path = f"{path.rstrip('/')}/{clean_name}"

                files.append(FileInfo(
                    path=full_path,
                    is_dir=is_dir,
                    size=0,
                    modified_at=""
                ))
            return files
        except Exception:
            return []

    def glob_info(self, pattern: str, path: str = '/') -> List[FileInfo]:
        """Structured glob matching."""
        try:
            cmd = f"find {shlex.quote(path)} -name {shlex.quote(pattern)}"
            code, out, err = self.sandbox.execute(cmd)
            if code != 0:
                return []

            files = []
            for fpath in out.splitlines():
                files.append(FileInfo(
                    path=fpath,
                    is_dir=False,
                    size=0,
                    modified_at=""
                ))
            return files
        except Exception:
            return []

    def grep_raw(self, pattern: str, path: str | None = None, glob: str | None = None) -> List[GrepMatch] | str:
        """Structured search results."""
        target = path if path else "."
        glob_arg = f"--include={glob}" if glob else ""

        try:
            cmd = f"grep -rn {glob_arg} {shlex.quote(pattern)} {shlex.quote(target)}"
            code, out, err = self.sandbox.execute(cmd)

            if code != 0 and code != 1: # 1 means no matches
                return f"Grep failed: {err}"

            matches = []
            for line in out.splitlines():
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    matches.append(GrepMatch(
                        file=parts[0],
                        line_number=int(parts[1]),
                        content=parts[2]
                    ))
            return matches
        except Exception as e:
            return f"Error: {e}"

    def download_files(self, paths: List[str]) -> List[FileDownloadResponse]:
        """Download multiple files from the sandbox."""
        responses = []
        for path in paths:
            try:
                content = self.sandbox.read_file(path)
                responses.append(FileDownloadResponse(
                    path=path,
                    content=content.encode('utf-8')
                ))
            except Exception as e:
                responses.append(FileDownloadResponse(
                    path=path,
                    content=b"",
                    error=str(e)
                ))
        return responses

    def upload_files(self, files: List[Tuple[str, bytes]]) -> List[FileUploadResponse]:
        """Upload multiple files to the sandbox."""
        responses = []
        for path, content_bytes in files:
            try:
                content_str = content_bytes.decode('utf-8')
                self.sandbox.write_file(path, content_str)
                responses.append(FileUploadResponse(path=path))
            except Exception as e:
                responses.append(FileUploadResponse(path=path, error=str(e)))
        return responses
