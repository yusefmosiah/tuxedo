from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from backend.vibewriter.sandbox.interface import SandboxInterface

class SandboxToolBase(BaseTool):
    """Base class for tools that operate within the sandbox."""
    sandbox: SandboxInterface = Field(description="The sandbox interface")

class TerminalTool(SandboxToolBase):
    name: str = "terminal"
    description: str = "Run shell commands in the sandbox. Use this to execute scripts, manage files, or run curl."

    def _run(self, command: str) -> str:
        code, out, err = self.sandbox.execute(command)
        if code != 0:
            return f"EXIT CODE: {code}\nSTDOUT:\n{out}\nSTDERR:\n{err}"
        return out

class FileReadTool(SandboxToolBase):
    name: str = "read_file"
    description: str = "Read the content of a file from the sandbox."

    def _run(self, file_path: str) -> str:
        try:
            return self.sandbox.read_file(file_path)
        except Exception as e:
            return f"Error reading file: {str(e)}"

class FileWriteTool(SandboxToolBase):
    name: str = "write_file"
    description: str = "Write content to a file in the sandbox. Overwrites if exists."

    def _run(self, file_path: str, content: str) -> str:
        try:
            self.sandbox.write_file(file_path, content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

class FileListTool(SandboxToolBase):
    name: str = "ls"
    description: str = "List files in a directory."

    def _run(self, path: str = ".") -> str:
        code, out, err = self.sandbox.execute(f"ls -F {path}")
        if code != 0:
            return f"Error: {err}"
        return out
