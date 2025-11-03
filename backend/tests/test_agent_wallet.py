"""
Agent Wallet Functionality Tests
Comprehensive tests for agent account management system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json

# Test fixtures
@pytest.fixture
def mock_key_manager():
    """Mock key manager for testing"""
    manager = Mock()
    manager.create_random_keypair = Mock()
    manager.store = Mock()
    manager.list_accounts = Mock(return_value=[])
    manager.has_account = Mock(return_value=True)
    manager.get_account_metadata = Mock(return_value={"name": "Test Account"})
    return manager

@pytest.fixture
def mock_stellar_server():
    """Mock Stellar server for testing"""
    server = Mock()
    account = Mock()
    account.balances = [
        Mock(asset_type="native", balance="1000.0")
    ]
    server.load_account = Mock(return_value=account)
    return server

@pytest.fixture
def mock_requests():
    """Mock requests for friendbot funding"""
    with patch('tools.agent.account_management.requests') as mock_req:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_req.get.return_value = mock_response
        yield mock_req

# Test agent account management tools
class TestAgentAccountManagement:
    """Test agent account management functionality"""

    @pytest.mark.asyncio
    async def test_create_agent_account_success(self, mock_key_manager, mock_stellar_server, mock_requests):
        """Test successful agent account creation"""
        with patch('tools.agent.account_management.KeyManager', return_value=mock_key_manager), \
             patch('tools.agent.account_management.Server', return_value=mock_stellar_server):

            from tools.agent.account_management import create_agent_account

            # Setup mock keypair
            mock_keypair = Mock()
            mock_keypair.public_key = "GDTEST123456789"
            mock_keypair.secret = "SDTEST123456789"
            mock_key_manager.create_random_keypair.return_value = mock_keypair

            result = create_agent_account("Test Account")

            assert result["success"] is True
            assert result["address"] == "GDTEST123456789"
            assert result["name"] == "Test Account"
            assert result["network"] == "testnet"
            assert result["funded"] is True

            mock_key_manager.store.assert_called_once_with("GDTEST123456789", "SDTEST123456789")
            mock_requests.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_agent_account_default_name(self, mock_key_manager, mock_stellar_server, mock_requests):
        """Test agent account creation with default name"""
        with patch('tools.agent.account_management.KeyManager', return_value=mock_key_manager), \
             patch('tools.agent.account_management.Server', return_value=mock_stellar_server):

            from tools.agent.account_management import create_agent_account

            # Setup mock keypair
            mock_keypair = Mock()
            mock_keypair.public_key = "GDTEST123456789"
            mock_keypair.secret = "SDTEST123456789"
            mock_key_manager.create_random_keypair.return_value = mock_keypair

            result = create_agent_account()

            assert result["success"] is True
            assert result["name"] == "Account 1"  # Default naming

    @pytest.mark.asyncio
    async def test_create_agent_account_funding_failure(self, mock_key_manager, mock_stellar_server):
        """Test agent account creation with funding failure"""
        with patch('tools.agent.account_management.KeyManager', return_value=mock_key_manager), \
             patch('tools.agent.account_management.Server', return_value=mock_stellar_server), \
             patch('tools.agent.account_management.requests') as mock_requests:

            from tools.agent.account_management import create_agent_account

            # Setup mock keypair
            mock_keypair = Mock()
            mock_keypair.public_key = "GDTEST123456789"
            mock_keypair.secret = "SDTEST123456789"
            mock_key_manager.create_random_keypair.return_value = mock_keypair

            # Mock funding failure
            mock_requests.get.side_effect = Exception("Funding failed")

            result = create_agent_account("Test Account")

            assert result["success"] is True  # Account still created, just not funded
            assert result["funded"] is False

    @pytest.mark.asyncio
    async def test_list_agent_accounts_empty(self, mock_key_manager, mock_stellar_server):
        """Test listing agent accounts when none exist"""
        with patch('tools.agent.account_management.KeyManager', return_value=mock_key_manager), \
             patch('tools.agent.account_management.Server', return_value=mock_stellar_server):

            from tools.agent.account_management import list_agent_accounts

            mock_key_manager.list_accounts.return_value = []

            result = list_agent_accounts()

            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_list_agent_accounts_with_balances(self, mock_key_manager, mock_stellar_server):
        """Test listing agent accounts with balances"""
        with patch('tools.agent.account_management.KeyManager', return_value=mock_key_manager), \
             patch('tools.agent.account_management.Server', return_value=mock_stellar_server):

            from tools.agent.account_management import list_agent_accounts

            mock_key_manager.list_accounts.return_value = ["GDTEST123456789", "GDTEST987654321"]

            result = list_agent_accounts()

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["address"] == "GDTEST123456789"
            assert result[0]["balance"] == 1000.0
            assert result[1]["address"] == "GDTEST987654321"
            assert result[1]["balance"] == 1000.0

    @pytest.mark.asyncio
    async def test_get_agent_account_info_success(self, mock_key_manager, mock_stellar_server):
        """Test getting agent account info successfully"""
        with patch('tools.agent.account_management.KeyManager', return_value=mock_key_manager), \
             patch('tools.agent.account_management.Server', return_value=mock_stellar_server):

            from tools.agent.account_management import get_agent_account_info

            mock_key_manager.has_account.return_value = True
            mock_key_manager.get_account_metadata.return_value = {
                "name": "Test Account",
                "created_at": "2025-01-03T00:00:00Z"
            }

            result = get_agent_account_info("GDTEST123456789")

            assert result["success"] is True
            assert result["address"] == "GDTEST123456789"
            assert result["balance"] == 1000.0
            assert result["metadata"]["name"] == "Test Account"

    @pytest.mark.asyncio
    async def test_get_agent_account_info_not_found(self, mock_key_manager, mock_stellar_server):
        """Test getting info for non-existent agent account"""
        with patch('tools.agent.account_management.KeyManager', return_value=mock_key_manager), \
             patch('tools.agent.account_management.Server', return_value=mock_stellar_server):

            from tools.agent.account_management import get_agent_account_info

            mock_key_manager.has_account.return_value = False

            result = get_agent_account_info("GDNOTFOUND123456")

            assert result["success"] is False
            assert "not found" in result["error"]

# Test LangChain tools
class TestAgentLangChainTools:
    """Test LangChain tool wrappers"""

    @pytest.mark.asyncio
    async def test_agent_create_account_tool(self, mock_key_manager, mock_stellar_server, mock_requests):
        """Test agent_create_account LangChain tool"""
        with patch('agent.tools.AGENT_ACCOUNT_TOOLS_AVAILABLE', True), \
             patch('agent.tools.create_agent_account') as mock_create:

            from agent.tools import agent_create_account

            # Setup mock result
            mock_create.return_value = {
                "success": True,
                "address": "GDTEST123456789",
                "name": "Test Account",
                "network": "testnet",
                "funded": True
            }

            result = await agent_create_account("Test Account")

            assert "🤖 Agent Account Created" in result
            assert "GDTEST123456789" in result
            assert "Test Account" in result
            mock_create.assert_called_once_with("Test Account")

    @pytest.mark.asyncio
    async def test_agent_list_accounts_tool(self, mock_key_manager, mock_stellar_server):
        """Test agent_list_accounts LangChain tool"""
        with patch('agent.tools.AGENT_ACCOUNT_TOOLS_AVAILABLE', True), \
             patch('agent.tools.list_agent_accounts') as mock_list:

            from agent.tools import agent_list_accounts

            # Setup mock result
            mock_list.return_value = [
                {
                    "address": "GDTEST123456789",
                    "name": "Test Account",
                    "balance": 1000.0,
                    "network": "testnet"
                }
            ]

            result = await agent_list_accounts()

            assert "🤖 Agent Accounts (1 accounts)" in result
            assert "GDTEST123456789" in result
            assert "1000.00 XLM" in result
            mock_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_get_account_info_tool(self, mock_key_manager, mock_stellar_server):
        """Test agent_get_account_info LangChain tool"""
        with patch('agent.tools.AGENT_ACCOUNT_TOOLS_AVAILABLE', True), \
             patch('agent.tools.get_agent_account_info') as mock_get:

            from agent.tools import agent_get_account_info

            # Setup mock result
            mock_get.return_value = {
                "success": True,
                "address": "GDTEST123456789",
                "balance": 1000.0,
                "network": "testnet",
                "metadata": {"name": "Test Account"}
            }

            result = await agent_get_account_info("GDTEST123456789")

            assert "🤖 Agent Account Information" in result
            assert "GDTEST123456789" in result
            assert "1000.00 XLM" in result
            mock_get.assert_called_once_with("GDTEST123456789")

# Test API endpoints
class TestAgentAPI:
    """Test agent API endpoints"""

    @pytest.mark.asyncio
    async def test_create_account_endpoint(self):
        """Test POST /api/agent/create-account endpoint"""
        with patch('api.routes.agent.AGENT_TOOLS_AVAILABLE', True), \
             patch('api.routes.agent.create_agent_account') as mock_create:

            from api.routes.agent import create_account
            from api.routes.agent import AccountCreateRequest

            # Setup mock result
            mock_create.return_value = {
                "address": "GDTEST123456789",
                "name": "Test Account",
                "balance": 1000.0,
                "network": "testnet",
                "funded": True
            }

            request = AccountCreateRequest(name="Test Account")
            result = await create_account(request)

            assert result.address == "GDTEST123456789"
            assert result.name == "Test Account"
            mock_create.assert_called_once_with("Test Account")

    @pytest.mark.asyncio
    async def test_list_accounts_endpoint(self):
        """Test GET /api/agent/accounts endpoint"""
        with patch('api.routes.agent.AGENT_TOOLS_AVAILABLE', True), \
             patch('api.routes.agent.list_agent_accounts') as mock_list:

            from api.routes.agent import list_accounts

            # Setup mock result
            mock_list.return_value = [
                {
                    "address": "GDTEST123456789",
                    "name": "Test Account",
                    "balance": 1000.0,
                    "network": "testnet"
                }
            ]

            result = await list_accounts()

            assert len(result) == 1
            assert result[0].address == "GDTEST123456789"
            mock_list.assert_called_once()

# Test integration scenarios
class TestAgentIntegration:
    """Test agent integration scenarios"""

    @pytest.mark.asyncio
    async def test_agent_account_creation_workflow(self):
        """Test complete agent account creation workflow"""
        # This would test the full flow from API to tool to blockchain
        # Mock all external dependencies
        with patch('tools.agent.account_management.KeyManager') as mock_km_class, \
             patch('tools.agent.account_management.Server') as mock_server_class, \
             patch('tools.agent.account_management.requests') as mock_requests:

            from tools.agent.account_management import create_agent_account

            # Setup mocks
            mock_km = Mock()
            mock_km_class.return_value = mock_km

            mock_keypair = Mock()
            mock_keypair.public_key = "GDTEST123456789"
            mock_keypair.secret = "SDTEST123456789"
            mock_km.create_random_keypair.return_value = mock_keypair
            mock_km.list_accounts.return_value = ["GDTEST123456789"]

            mock_server = Mock()
            mock_server_class.return_value = mock_server

            mock_response = Mock()
            mock_response.status_code = 200
            mock_requests.get.return_value = mock_response

            # Test account creation
            result = create_agent_account("Integration Test Account")

            assert result["success"] is True
            assert result["address"] == "GDTEST123456789"
            assert result["name"] == "Integration Test Account"

            # Test listing accounts
            from tools.agent.account_management import list_agent_accounts
            accounts = list_agent_accounts()

            assert len(accounts) == 1
            assert accounts[0]["address"] == "GDTEST123456789"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])