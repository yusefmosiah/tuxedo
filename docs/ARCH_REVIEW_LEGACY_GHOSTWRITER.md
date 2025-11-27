# Architecture Review: Ghostwriter Pipeline Workspace Management

## 1. Current Architecture

The Ghostwriter pipeline, implemented in `backend/agent/ghostwriter/pipeline.py`, currently uses the `openhands.sdk.LocalWorkspace` to manage the execution environment for its research and writing agents.

The `LocalWorkspace` creates a new directory on the local filesystem for each session, located under a root directory specified by the `workspace_root` parameter. The default value for this parameter is `ghostwriter_sessions`, which is a relative path.

The `main` function in `pipeline.py` hardcodes this path to `/workspace/ghostwriter_sessions`.

### 1.1. Problems with the Current Architecture

1.  **PermissionsError:** The use of `LocalWorkspace` can lead to `PermissionsError` if the user running the application does not have write permissions to the `workspace_root` directory. This is especially problematic when the path is hardcoded to a system-level directory like `/workspace`, as is the case in the `main` function.

2.  **Lack of Isolation:** The `LocalWorkspace` does not provide any isolation between the agent's execution environment and the host system. This means that the agent has full access to the filesystem and other resources of the host, which can be a security risk.

3.  **Dependency Management:** The `LocalWorkspace` does not manage dependencies for the agent. This means that all dependencies must be installed on the host system, which can lead to conflicts and make it difficult to reproduce the agent's environment.

## 2. Proposed Architecture: Docker-based Workspaces

To address the problems with the current architecture, I propose to use the `openhands.workspace.DockerWorkspace` to manage the execution environment for the Ghostwriter agents.

The `DockerWorkspace` runs the agent in an isolated Docker container, which provides a secure and reproducible environment.

### 2.1. Benefits of the Proposed Architecture

1.  **Security:** The `DockerWorkspace` provides a secure sandbox for the agent, which prevents it from accessing the host system's resources.

2.  **Reproducibility:** The `DockerWorkspace` makes it easy to reproduce the agent's environment by specifying a Docker image with all the necessary dependencies.

3.  **Scalability:** The `DockerWorkspace` makes it easy to scale the Ghostwriter pipeline by running multiple agents in parallel on different machines.

## 3. Implementation Plan

To implement the proposed architecture, I will perform the following steps:

1.  **Update `pipeline.py` to use `DockerWorkspace`:** I will modify the `GhostwriterPipeline` class to use the `DockerWorkspace` instead of the `LocalWorkspace`. This will involve the following changes:
    *   Import the `DockerWorkspace` class from the `openhands.workspace` module.
    *   Update the `__init__` method to accept a `base_image` parameter, which will be used to specify the Docker image for the agent's environment.
    *   Update the `create_session` method to create a new `DockerWorkspace` for each session.
    *   Update the `_run_single_researcher` method to pass the `DockerWorkspace` to the `Conversation` object.
2.  **Create a Docker image for the Ghostwriter agent:** I will create a new `Dockerfile` that defines the environment for the Ghostwriter agent. This will include the following:
    *   A base image with Python and other necessary dependencies.
    *   The Ghostwriter agent code.
    *   Any other necessary files, such as prompts and style guides.
3.  **Update the `main` function to use the new architecture:** I will update the `main` function in `pipeline.py` to use the new `DockerWorkspace`-based architecture. This will involve the following changes:
    *   Remove the hardcoded `workspace_root` parameter.
    *   Pass a `base_image` parameter to the `GhostwriterPipeline` constructor.

## 4. Risks and Mitigations

1.  **Docker Installation:** The proposed architecture requires Docker to be installed on the host system. To mitigate this risk, I will add a check to the `GhostwriterPipeline` class that raises an exception if Docker is not installed.
2.  **Docker Image Size:** The Docker image for the Ghostwriter agent may be large, which can increase the startup time for the pipeline. To mitigate this risk, I will use a minimal base image and only include the necessary dependencies in the image.
