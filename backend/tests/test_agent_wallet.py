"""
Agent Wallet Functionality Tests
Comprehensive tests for agent account management system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json

# Test API endpoints
class TestAgentAPI:
    """Test agent API endpoints"""

    def test_create_account_endpoint(self, test_client):
        """Test POST /api/agent/create-account endpoint"""
        with patch('api.routes.agent.create_agent_account') as mock_create:
            # Setup mock result
            mock_create.return_value = {
                "address": "GDTEST123456789",
                "name": "Test Account",
                "balance": 1000.0,
                "network": "mainnet",
                "funded": True,
                "success": True,
            }

            response = test_client.post("/api/agent/create-account", json={"name": "Test Account"})

            assert response.status_code == 200
            data = response.json()
            assert data["address"] == "GDTEST123456789"
            assert data["name"] == "Test Account"
            mock_create.assert_called_once()

    def test_list_accounts_endpoint(self, test_client):
        """Test GET /api/agent/accounts endpoint"""
        with patch('api.routes.agent.list_agent_accounts') as mock_list:
            # Setup mock result
            mock_list.return_value = [
                {
                    "address": "GDTEST123456789",
                    "name": "Test Account",
                    "balance": 1000.0,
                    "network": "mainnet"
                }
            ]

            response = test_client.get("/api/agent/accounts")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["address"] == "GDTEST123456789"
            mock_list.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
