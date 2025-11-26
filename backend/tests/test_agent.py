#!/usr/bin/env python3
"""
Test script for the LLM Agent integration
"""

import asyncio
import json

def test_agent_stellar_query(test_client):
    """Test the LLM agent with a simple Stellar query"""
    print("\n📊 Test 1: Query Stellar network status")
    response = test_client.post("/chat", json={
        "message": "What's the current Stellar network status and fee information?",
        "history": [],
        "wallet_address": None
    })
    assert response.status_code == 200
    result = response.json()
    print("✅ Success!")
    print(f"Agent Response: {result['response'][:200]}...")

def test_agent_create_account(test_client):
    """Test the LLM agent's account creation tool"""
    print("\n👤 Test 2: Create a mainnet account")
    response = test_client.post("/chat", json={
        "message": "Please create a new Stellar account for me",
        "history": [],
        "wallet_address": None
    })
    assert response.status_code == 200
    result = response.json()
    print("✅ Success!")
    print(f"Agent Response: {result['response'][:200]}...")

def test_agent_market_data(test_client):
    """Test the LLM agent's market data tool"""
    print("\n📈 Test 3: Query market data for XLM/USDC")
    response = test_client.post("/chat", json={
        "message": "Can you show me the current orderbook for XLM/USDC on the Stellar DEX?",
        "history": [],
        "wallet_address": None
    })
    assert response.status_code == 200
    result = response.json()
    print("✅ Success!")
    print(f"Agent Response: {result['response'][:200]}...")

if __name__ == "__main__":
    # This test must be run with pytest
    print("This test must be run with pytest.")
