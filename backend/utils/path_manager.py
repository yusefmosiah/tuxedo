"""
Persistent Path Manager for Phala CVM Deployment

Handles path resolution for development vs production environments.
In local development, uses relative paths.
In Phala CVM, uses /app/data persistent volume.
"""
import os
from pathlib import Path
from typing import Optional


class PersistentPathManager:
    """Manages filesystem paths for multi-environment deployment."""

    # Environment detection
    IS_PHALA = os.getenv("PHALA_DEPLOYMENT", "false").lower() == "true"

    # Base directories
    if IS_PHALA:
        BASE_DIR = Path("/app/data")
        CODE_DIR = Path("/app/code")
    else:
        # Local development
        BASE_DIR = Path(__file__).parent.parent.parent / "data"
        CODE_DIR = Path(__file__).parent.parent

    # Create base directory if it doesn't exist
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def workspace_dir(cls, user_id: str, session_id: str) -> Path:
        """
        Get workspace directory for a specific user session.

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Path to workspace directory
        """
        workspace_path = cls.BASE_DIR / "workspaces" / user_id / session_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        return workspace_path

    @classmethod
    def user_workspace_root(cls, user_id: str) -> Path:
        """
        Get root workspace directory for a user (all sessions).

        Args:
            user_id: User identifier

        Returns:
            Path to user's workspace root
        """
        user_path = cls.BASE_DIR / "workspaces" / user_id
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path

    @classmethod
    def db_path(cls, db_name: str) -> Path:
        """
        Get database file path.

        Args:
            db_name: Database filename (e.g., "users.db")

        Returns:
            Path to database file
        """
        db_dir = cls.BASE_DIR / "db"
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / db_name

    @classmethod
    def session_dir(cls, session_id: str, user_id: Optional[str] = None) -> Path:
        """
        Get session directory (legacy compatibility).

        Args:
            session_id: Session identifier
            user_id: Optional user identifier (defaults to "default")

        Returns:
            Path to session directory
        """
        user = user_id or "default"
        return cls.workspace_dir(user, session_id)

    @classmethod
    def ensure_structure(cls):
        """Create all required directory structures."""
        directories = [
            cls.BASE_DIR / "db",
            cls.BASE_DIR / "workspaces",
            cls.BASE_DIR / "logs",
            cls.BASE_DIR / "cache",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_config(cls) -> dict:
        """Get current path configuration for debugging."""
        return {
            "is_phala": cls.IS_PHALA,
            "base_dir": str(cls.BASE_DIR),
            "code_dir": str(cls.CODE_DIR),
            "exists": {
                "base_dir": cls.BASE_DIR.exists(),
                "db_dir": (cls.BASE_DIR / "db").exists(),
                "workspaces_dir": (cls.BASE_DIR / "workspaces").exists(),
            }
        }


# Initialize directory structure on import
PersistentPathManager.ensure_structure()
