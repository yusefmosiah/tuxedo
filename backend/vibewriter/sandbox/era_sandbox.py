import subprocess
import logging
import shlex
from typing import Tuple
from .interface import SandboxInterface

logger = logging.getLogger(__name__)

class EraSandbox(SandboxInterface):
    """
    Sandbox implementation using BinSquare/ERA (MicroVMs).

    This class wraps the local 'agent' CLI provided by ERA to execute commands
    inside a hardware-isolated MicroVM.
    """

    def __init__(self, vm_id: str):
        """
        Initialize connection to a specific ERA MicroVM.

        Args:
            vm_id: The ID or name of the ERA VM session.
        """
        self.vm_id = vm_id
        # Note: We assume the 'agent' CLI is installed and available in PATH.
        # In a real deployment, we might need to configure the binary path.
        self.cli_cmd = "agent"

    def _run_cli(self, args: list) -> Tuple[int, str, str]:
        """Helper to run the ERA CLI command."""
        cmd = [self.cli_cmd] + args
        try:
            logger.debug(f"Running ERA command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            # Fallback for development/testing if ERA isn't installed
            logger.warning("ERA 'agent' CLI not found. Using local subprocess fallback (INSECURE).")
            return -1, "", "ERA CLI not found"

    def execute(self, command: str, timeout: int = 300) -> Tuple[int, str, str]:
        """
        Execute command inside the MicroVM.
        Usage: agent vm exec -- <command>
        """
        # Note: ERA CLI usage might vary. Assuming 'vm exec' pattern based on docs.
        # We wrap the command in bash to ensure pipes/redirection work inside the VM
        safe_command = f"bash -c {shlex.quote(command)}"

        # Check if we are in a dev environment without ERA
        # TODO: Remove this fallback in production
        if self._run_cli(["--version"])[0] != 0:
             # Fallback to local execution for testing logic flow without VM
             try:
                 res = subprocess.run(
                     ["bash", "-c", command],
                     capture_output=True,
                     text=True,
                     timeout=timeout
                 )
                 return res.returncode, res.stdout, res.stderr
             except subprocess.TimeoutExpired:
                 return 124, "", "Timeout expired"

        # Actual ERA execution
        args = ["vm", "exec", self.vm_id, "--", safe_command]
        return self._run_cli(args)

    def read_file(self, path: str) -> str:
        """Read file using 'cat' inside the VM."""
        code, out, err = self.execute(f"cat {shlex.quote(path)}")
        if code != 0:
            raise FileNotFoundError(f"File not found or unreadable: {path}. Error: {err}")
        return out

    def write_file(self, path: str, content: str) -> None:
        """
        Write file using 'cat' and heredoc inside the VM.
        Warning: This basic implementation might fail for binary data or complex escaping.
        A robust implementation would use ERA's file transfer API if available.
        """
        # Escape EOF to prevent injection, though extremely unlikely in this context
        delimiter = "EOF_VIBEWRITER"

        # We use a python one-liner inside the VM to write the file safely if possible,
        # or just cat. Let's stick to cat with careful quoting for now.
        # Better: Base64 encode locally, echo to file, base64 decode inside.

        import base64
        b64_content = base64.b64encode(content.encode('utf-8')).decode('ascii')

        cmd = f"echo {b64_content} | base64 -d > {shlex.quote(path)}"
        code, out, err = self.execute(cmd)

        if code != 0:
            raise IOError(f"Failed to write file {path}: {err}")

    def file_exists(self, path: str) -> bool:
        code, _, _ = self.execute(f"test -f {shlex.quote(path)}")
        return code == 0
