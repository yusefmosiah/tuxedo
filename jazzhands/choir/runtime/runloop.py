from typing import Any
from openhands.runtime.impl.remote.remote_runtime import RemoteRuntime
from .base import ChoirRuntime

class RunLoopChoirRuntime(RemoteRuntime, ChoirRuntime):
    """
    RunLoop implementation of ChoirRuntime.
    """

    def __init__(
        self,
        user_id: str,
        config: Any,
        event_stream: Any,
        llm_registry: Any,
        **kwargs
    ):
        super().__init__(
            config=config,
            event_stream=event_stream,
            llm_registry=llm_registry,
            user_id=user_id,
            **kwargs
        )

    @property
    def user_id(self) -> str:
        return getattr(self, "_user_id", "")

    @user_id.setter
    def user_id(self, value: str):
        self._user_id = value

    async def connect(self):
        await super().connect()

    async def run_action(self, action: Any) -> Any:
        pass

    async def close(self):
        await super().close()
