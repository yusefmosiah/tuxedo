#!/usr/bin/env python3
"""
Live Summary Service for Tuxedo AI Chat Interface

Provides real-time summarization of streaming AI responses to minimize
cognitive load while maintaining full transparency.
"""

import os
import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger(__name__)

class LiveSummaryService:
    """Service for generating live summaries of AI conversations."""

    def __init__(self):
        """Initialize the live summary service."""
        self.summarization_model = os.getenv('SUMMARIZATION_MODEL', 'gpt-4o-mini')
        self.primary_model = os.getenv('PRIMARY_MODEL', 'gpt-4o')

        # Initialize the live summary LLM (try same config as final summary)
        self.summary_llm = ChatOpenAI(
            model=self.summarization_model,
            temperature=0.1,  # Even lower temperature for consistency
            max_tokens=150,   # Same as final summary
        )

        # Initialize the final summary LLM
        self.final_summary_llm = ChatOpenAI(
            model=self.summarization_model,
            temperature=0.3,
            max_tokens=150,   # Longer for final summaries
        )

        logger.info(f"LiveSummaryService initialized with model: {self.summarization_model}")

    async def generate_live_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Generate a concise live summary (max 60 characters) of current progress.

        Args:
            messages: List of streaming messages in this conversation segment

        Returns:
            Concise summary string (max 60 characters)
        """
        if not messages:
            return "Processing your request..."

        try:
            # Extract relevant content from messages
            relevant_content = self._extract_relevant_content(messages)

            if not relevant_content:
                return "Working on your request..."

            # Create the live summary prompt
            prompt = self._create_live_summary_prompt(relevant_content)

            # Generate summary
            response = await self.summary_llm.ainvoke([
                SystemMessage(content="You are creating brief, real-time progress updates for a Stellar AI assistant. Keep responses under 60 characters. Use present tense. Be concise and clear."),
                HumanMessage(content=prompt)
            ])

            summary = response.content.strip()

            # Ensure it's not too long
            if len(summary) > 60:
                summary = summary[:57] + "..."

            logger.info(f"Generated live summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error generating live summary: {e}")
            return "Processing your request..."

    async def generate_final_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive final summary of the conversation segment.

        Args:
            messages: List of all messages in this conversation segment

        Returns:
            Comprehensive summary string (max 100 words)
        """
        if not messages:
            return "No significant activity to summarize."

        try:
            # Extract embedded transactions BEFORE summarization
            embedded_transactions = []
            for msg in messages:
                content = msg.get('content', '')
                if '[STELLAR_TX]' in content:
                    import re
                    tx_matches = re.findall(r'\[STELLAR_TX\](.*?)\[/STELLAR_TX\]', content, re.DOTALL)
                    embedded_transactions.extend(tx_matches)
                    logger.info(f"Found {len(tx_matches)} embedded transaction(s) in message")

            # Extract all relevant content
            relevant_content = self._extract_relevant_content(messages)

            if not relevant_content:
                return "Completed processing your request."

            # Create the final summary prompt
            prompt = self._create_final_summary_prompt(relevant_content)

            # Generate summary
            response = await self.final_summary_llm.ainvoke([
                SystemMessage(content="You are creating comprehensive summaries of Stellar AI conversations. Focus on key findings, important tool outputs, action items completed, and final outcomes. Maximum 100 words."),
                HumanMessage(content=prompt)
            ])

            summary = response.content.strip()

            # Ensure it's not too long (roughly 100 words)
            if len(summary.split()) > 100:
                summary = ' '.join(summary.split()[:97]) + "..."

            # Append embedded transactions to the end of the summary
            if embedded_transactions:
                for tx in embedded_transactions:
                    summary += f"\n\n[STELLAR_TX]{tx}[/STELLAR_TX]"
                logger.info(f"Appended {len(embedded_transactions)} transaction(s) to summary")

            logger.info(f"Generated final summary with transactions: {len(summary)} chars")
            return summary

        except Exception as e:
            logger.error(f"Error generating final summary: {e}")
            return "Completed processing your request."

    async def generate_tool_summary(self, tool_name: str, tool_content: str) -> str:
        """
        Generate a concise summary of a tool result for display in the chat interface.

        Args:
            tool_name: Name of the tool that was executed
            tool_content: Raw content/output from the tool

        Returns:
            Concise summary of the tool result (max 80 characters)
        """
        if not tool_content:
            return f"{tool_name} executed"

        try:
            # Create a focused prompt for tool summarization
            prompt = f"""Tool: {tool_name}
Output: {tool_content[:1000]}  # Limit content to prevent token overflow

Create a very concise summary (max 80 characters) of what this tool accomplished.
Focus on the key result or information obtained.
Use present tense when possible.

Examples:
- "Account GABCD... created with 10,000 XLM"
- "XLM/USDC price: $0.1234"
- "Trustline for USDC established"
- "Network status: active"

Summary:"""

            # Generate summary using a more focused model configuration
            summary_llm = ChatOpenAI(
                model=self.summarization_model,
                temperature=0.1,
                max_tokens=60,  # Very concise
            )

            response = await summary_llm.ainvoke([
                SystemMessage(content="You are creating ultra-concise summaries of Stellar tool results. Maximum 80 characters. Focus on key outcomes only."),
                HumanMessage(content=prompt)
            ])

            summary = response.content.strip()

            # Ensure it's not too long
            if len(summary) > 80:
                summary = summary[:77] + "..."

            logger.info(f"Generated tool summary for {tool_name}: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error generating tool summary: {e}")
            # Fallback to simple truncation
            return f"{tool_name}: " + (tool_content[:40] + "..." if len(tool_content) > 40 else tool_content)

    def _extract_relevant_content(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract relevant content from streaming messages."""
        relevant_content = []

        for msg in messages:
            # Skip thinking messages and focus on actual content
            if msg.get('type') in ['thinking', 'tool_call_start']:
                continue

            content = msg.get('content', '').strip()
            if content and content.lower() not in ['thinking...', 'processing...']:
                # Add tool name if present
                tool_name = msg.get('tool_name')
                if tool_name and content.lower() != tool_name:
                    relevant_content.append(f"[{tool_name}] {content}")
                else:
                    relevant_content.append(content)

        return relevant_content

    def _create_live_summary_prompt(self, content: List[str]) -> str:
        """Create a prompt for live summary generation."""
        recent_content = content[-3:] if len(content) > 3 else content  # Focus on last 3 items

        prompt = f"""You are creating a brief status update for a Stellar AI assistant.

Recent activity:
{chr(10).join(f"- {item}" for item in recent_content)}

Create a status update following these rules:
- Maximum 60 characters
- Present tense (is/are verbs)
- Focus on current action
- Must be a complete phrase
- Examples: "Creating account...", "Checking network status...", "Querying data..."

Status update:"""

        return prompt

    def _create_final_summary_prompt(self, content: List[str]) -> str:
        """Create a prompt for final summary generation."""
        prompt = f"""Create a comprehensive summary (max 100 words) of this Stellar AI conversation:

All activity:
{chr(10).join(f"- {item}" for item in content)}

Focus on:
- Key findings and results
- Important tool outputs and values (account numbers, balances, prices, etc.)
- Actions completed successfully
- Final outcomes

This summary will be permanent in the conversation history.

Summary:"""

        return prompt

# Global instance
live_summary_service: Optional[LiveSummaryService] = None

def get_live_summary_service() -> LiveSummaryService:
    """Get the global live summary service instance."""
    global live_summary_service
    if live_summary_service is None:
        live_summary_service = LiveSummaryService()
    return live_summary_service

def is_live_summary_enabled() -> bool:
    """Check if live summary functionality is enabled."""
    return bool(os.getenv('SUMMARIZATION_MODEL')) and bool(os.getenv('OPENAI_API_KEY'))