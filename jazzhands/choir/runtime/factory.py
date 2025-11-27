from typing import Any
from .base import ChoirRuntime
from .runloop import RunLoopChoirRuntime
from .era import EraRuntime

class RuntimeFactory:
    """
    Factory to create the appropriate runtime implementation.
    """

    @staticmethod
    def create(
        user_id: str,
        provider: str = "runloop",
        config: Any = None,
        event_stream: Any = None,
        llm_registry: Any = None,
        **kwargs
    ) -> ChoirRuntime:
        if provider == "runloop":
            return RunLoopChoirRuntime(
                user_id=user_id,
                config=config,
                event_stream=event_stream,
                llm_registry=llm_registry,
                **kwargs
            )
        elif provider == "era":
            return EraRuntime(user_id=user_id, **kwargs)
        else:
            raise ValueError(f"Unknown runtime provider: {provider}")
