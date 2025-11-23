"""
Utility functions for ghostwriter pipeline.

Handles filesystem operations, session management, and checkpointing.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class SessionManager:
    """Manages filesystem structure and checkpointing for ghostwriter sessions."""

    def __init__(self, workspace_root: str = "/workspace/sessions"):
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.session_id: Optional[str] = None
        self.session_dir: Optional[Path] = None

    def create_session(self, topic: str) -> str:
        """Create new session with timestamp-based ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"
        self.session_dir = self.workspace_root / self.session_id

        # Create stage directories
        stage_dirs = [
            "00_research",
            "01_draft",
            "02_extraction",
            "03_verification",
            "04_critique",
            "05_revision",
            "06_re_verification",
            "07_style",
        ]

        for stage_dir in stage_dirs:
            (self.session_dir / stage_dir).mkdir(parents=True, exist_ok=True)

        # Save session metadata
        metadata = {
            "session_id": self.session_id,
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
        }
        self.save_json("metadata.json", metadata)

        # Create transcript file
        self.log(f"Session created: {self.session_id}")
        self.log(f"Topic: {topic}")

        return self.session_id

    def get_stage_dir(self, stage: str) -> Path:
        """Get path to stage directory."""
        if not self.session_dir:
            raise ValueError("No active session")
        return self.session_dir / stage

    def save_json(self, filename: str, data: Dict[str, Any]) -> Path:
        """Save JSON data to session directory."""
        if not self.session_dir:
            raise ValueError("No active session")

        filepath = self.session_dir / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        self.log(f"Saved JSON: {filename}")
        return filepath

    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON data from session directory."""
        if not self.session_dir:
            raise ValueError("No active session")

        filepath = self.session_dir / filename
        with open(filepath, "r") as f:
            return json.load(f)

    def save_text(self, filename: str, content: str) -> Path:
        """Save text file to session directory."""
        if not self.session_dir:
            raise ValueError("No active session")

        filepath = self.session_dir / filename
        with open(filepath, "w") as f:
            f.write(content)

        self.log(f"Saved text: {filename}")
        return filepath

    def load_text(self, filename: str) -> str:
        """Load text file from session directory."""
        if not self.session_dir:
            raise ValueError("No active session")

        filepath = self.session_dir / filename
        with open(filepath, "r") as f:
            return f.read()

    def log(self, message: str) -> None:
        """Append message to session transcript."""
        if not self.session_dir:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        transcript_path = self.session_dir / "transcript.txt"
        with open(transcript_path, "a") as f:
            f.write(log_message)

    def update_status(self, status: str, stage: Optional[str] = None) -> None:
        """Update session status in metadata."""
        try:
            metadata = self.load_json("metadata.json")
            metadata["status"] = status
            metadata["last_updated"] = datetime.now().isoformat()
            if stage:
                metadata["current_stage"] = stage
            self.save_json("metadata.json", metadata)
        except Exception as e:
            self.log(f"Warning: Could not update status: {e}")

    def checkpoint(self, stage: str, data: Dict[str, Any]) -> None:
        """Save checkpoint for stage (enables resumption)."""
        checkpoint_file = f"checkpoint_{stage}.json"
        checkpoint_data = {
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        self.save_json(checkpoint_file, checkpoint_data)
        self.log(f"Checkpoint saved: {stage}")

    def list_sessions(self) -> list[str]:
        """List all session IDs in workspace."""
        if not self.workspace_root.exists():
            return []
        return [d.name for d in self.workspace_root.iterdir() if d.is_dir()]

    def load_session(self, session_id: str) -> None:
        """Load existing session for resumption."""
        self.session_id = session_id
        self.session_dir = self.workspace_root / session_id

        if not self.session_dir.exists():
            raise ValueError(f"Session not found: {session_id}")

        self.log(f"Session loaded: {session_id}")


def format_source_markdown(
    url: str,
    title: str,
    date_published: str,
    date_accessed: str,
    source_type: str,
    excerpts: str,
    summary: str,
) -> str:
    """Format source data as markdown for research stage."""
    return f"""---
url: {url}
title: {title}
date_published: {date_published}
date_accessed: {date_accessed}
source_type: {source_type}
---

# Key Excerpts
{excerpts}

# Summary
{summary}
"""


def parse_source_markdown(content: str) -> Dict[str, str]:
    """Parse source markdown back into structured data."""
    lines = content.split("\n")
    metadata = {}
    in_metadata = False
    excerpts = []
    summary = []
    current_section = None

    for line in lines:
        if line.strip() == "---":
            in_metadata = not in_metadata
            continue

        if in_metadata:
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        elif line.startswith("# Key Excerpts"):
            current_section = "excerpts"
        elif line.startswith("# Summary"):
            current_section = "summary"
        elif current_section == "excerpts":
            excerpts.append(line)
        elif current_section == "summary":
            summary.append(line)

    return {
        **metadata,
        "excerpts": "\n".join(excerpts).strip(),
        "summary": "\n".join(summary).strip(),
    }
