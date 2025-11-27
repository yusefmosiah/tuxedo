from abc import ABC, abstractmethod
from typing import Any

class ChoirRuntime(ABC):
    """
    Abstract base class for Choir runtime environments.
    """

    @abstractmethod
    async def connect(self):
        """Establish connection to the runtime."""
        pass

    @abstractmethod
    async def run_action(self, action: Any) -> Any:
        """Execute an action."""
        pass

    @abstractmethod
    async def close(self):
        """Close the session."""
        pass

    @property
    @abstractmethod
    def user_id(self) -> str:
        """Return the user ID associated with this runtime."""
        pass
