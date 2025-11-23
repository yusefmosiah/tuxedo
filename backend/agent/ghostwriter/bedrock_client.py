"""
Direct AWS Bedrock client for Ghostwriter.

Bypasses the buggy Claude Agent SDK and uses direct HTTP API calls,
which we've proven work perfectly with your bearer token.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, AsyncIterator
import httpx

logger = logging.getLogger(__name__)


class BedrockClient:
    """
    Direct AWS Bedrock client using HTTP API.

    This bypasses the Claude Agent SDK's buggy subprocess integration
    and makes direct API calls to Bedrock, which work perfectly.
    """

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        region: str = "us-east-1"
    ):
        """
        Initialize Bedrock client.

        Args:
            bearer_token: AWS Bedrock API bearer token (defaults to AWS_BEARER_TOKEN_BEDROCK)
            region: AWS region (defaults to us-east-1)
        """
        self.bearer_token = bearer_token or os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

        if not self.bearer_token:
            raise ValueError("AWS_BEARER_TOKEN_BEDROCK not set")

        self.base_url = f"https://bedrock-runtime.{self.region}.amazonaws.com"
        logger.info(f"Bedrock client initialized (region: {self.region})")

    async def invoke_model(
        self,
        model_id: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 4096,
        temperature: float = 1.0,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke a Bedrock model.

        Args:
            model_id: Bedrock model ID (e.g., "anthropic.claude-3-haiku-20240307-v1:0")
            messages: List of message dicts with "role" and "content"
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            system: Optional system prompt

        Returns:
            API response with generated content
        """
        endpoint = f"{self.base_url}/model/{model_id}/invoke"

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(endpoint, headers=headers, json=payload)

            if response.status_code != 200:
                logger.error(f"Bedrock API error: {response.status_code} - {response.text}")
                raise Exception(f"Bedrock API error: {response.status_code} - {response.text}")

            return response.json()

    async def query_simple(
        self,
        prompt: str,
        model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        system: Optional[str] = None
    ) -> str:
        """
        Simple query interface - returns text response.

        Args:
            prompt: User prompt
            model_id: Bedrock model ID
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            system: Optional system prompt

        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]

        response = await self.invoke_model(
            model_id=model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system
        )

        # Extract text from response
        content = response.get("content", [])
        if content and len(content) > 0:
            return content[0].get("text", "")

        return ""


# Model ID constants for Bedrock
BEDROCK_HAIKU_3 = "anthropic.claude-3-haiku-20240307-v1:0"
BEDROCK_SONNET_3_5 = "anthropic.claude-3-5-sonnet-20241022-v2:0"
BEDROCK_HAIKU_3_5 = "anthropic.claude-3-5-haiku-20241022-v1:0"

# Preferred models for Ghostwriter
BEDROCK_MODEL_HAIKU = BEDROCK_HAIKU_3  # Fast and cheap for simple tasks
BEDROCK_MODEL_SONNET = BEDROCK_SONNET_3_5  # Complex reasoning
