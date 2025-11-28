# Vibewriter Deep Agent

This directory contains the implementation of the Vibewriter Deep Agent, powered by LangChain Deep Agents and Runloop.

## Setup

1.  **Dependencies**: Ensure `deepagents`, `runloop-api-client`, `langchain-anthropic` (or `langchain-openai` for OpenRouter) are installed.
    ```bash
    pip install deepagents runloop-api-client langchain-anthropic langchain-openai
    ```
2.  **Environment Variables**:
    -   `RUNLOOP_API_KEY`: Required for the sandbox environment.
    -   `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`: For the LLM.
    -   `TAVILY_API_KEY`: For web search capabilities.

## Architecture

-   **`agent.py`**: Contains the `VibewriterAgent` class. It initializes the LangChain agent with the Runloop backend and manages sub-agents.
-   **`runloop_backend.py`**: Adapts the Runloop API to the `deepagents.backends.protocol.SandboxBackendProtocol`.
-   **`tools.py`**: Custom tools for Vibewriter (Choir KB search, Citation, Publishing, Web Search).
-   **`subagents/`**: Contains definitions for specialized sub-agents:
    -   `researcher.py`: Handles web search and KB lookup.
    -   `writer.py`: Handles content drafting, citation, and publishing.

## Running Tests

There are several test scripts to verify the agent's functionality:

1.  **`test_connection.py`**: Verifies connectivity to the Runloop sandbox.
    ```bash
    python vibewriter/test_connection.py
    ```

2.  **`test_planning.py`**: Tests the agent's ability to plan, execute a simple task (write a haiku), and use filesystem operations (write/read files).
    ```bash
    python -m vibewriter.test_planning
    ```

3.  **`test_tools.py`**: Tests the specific Vibewriter tools (Research, Web Search, Citation, Publishing) in a workflow.
    ```bash
    python -m vibewriter.test_tools
    ```

4.  **`test_subagents.py`**: Tests the hierarchical delegation to Researcher and Writer sub-agents.
    ```bash
    python -m vibewriter.test_subagents
    ```

## Current Status

-   [x] Runloop Sandbox Integration
-   [x] Basic Agent Loop (Plan -> Act -> Observe)
-   [x] Filesystem Tools (ls, read, write, execute)
-   [x] Vibewriter Tools (Mocked KB/Publishing, Real Web Search)
