from abc import ABC, abstractmethod
from typing import Tuple

class SandboxInterface(ABC):
    """
    Abstract interface for a sandbox environment (MicroVM).

    This interface abstracts away the difference between running locally,
    using a local MicroVM (ERA/Firecracker), or using a remote service (RunLoop).
    """

    @abstractmethod
    def execute(self, command: str, timeout: int = 300) -> Tuple[int, str, str]:
        """
        Run a shell command in the sandbox.

        Args:
            command: The bash command to run.
            timeout: Execution timeout in seconds.

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        pass

    @abstractmethod
    def read_file(self, path: str) -> str:
        """
        Read file content from the sandbox.

        Args:
            path: Absolute path in the sandbox filesystem.

        Returns:
            File content as string.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        pass

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        """
        Write content to a file in the sandbox.

        Args:
            path: Absolute path in the sandbox filesystem.
            content: String content to write.
        """
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if a file exists in the sandbox."""
        pass
