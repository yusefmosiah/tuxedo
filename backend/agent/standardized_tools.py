"""
Standardized Tool Interface for Tuxedo AI
Addresses sync/async inconsistency and provides unified tool patterns
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, Callable
from pydantic import BaseModel, Field, validator
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# 1. STANDARDIZED TOOL INTERFACES
# ============================================================================

class ToolStatus(str, Enum):
    """Tool execution status"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    NETWORK_ERROR = "network_error"

class ToolResult(BaseModel):
    """Standardized result format for all tools"""
    status: ToolStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    tool_name: Optional[str] = None
    request_id: Optional[str] = None

    @classmethod
    def success(
        cls,
        data: Dict[str, Any] = None,
        execution_time: float = None,
        tool_name: str = None,
        **kwargs
    ) -> "ToolResult":
        """Create successful result"""
        return cls(
            status=ToolStatus.SUCCESS,
            data=data or {},
            execution_time=execution_time,
            tool_name=tool_name,
            **kwargs
        )

    @classmethod
    def error(
        cls,
        error: str,
        execution_time: float = None,
        tool_name: str = None,
        **kwargs
    ) -> "ToolResult":
        """Create error result"""
        return cls(
            status=ToolStatus.ERROR,
            error=error,
            execution_time=execution_time,
            tool_name=tool_name,
            **kwargs
        )

class BaseTool(ABC):
    """Abstract base class for all standardized tools"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description available"
        self.timeout = 30.0  # Default timeout in seconds
        self.max_retries = 3
        self.retry_delay = 1.0

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool operation. Must be implemented by subclasses.

        Returns:
            ToolResult: Standardized result object
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get tool schema for LangChain integration.

        Returns:
            Dict containing tool schema
        """
        pass

    def validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """
        Validate input parameters. Override in subclasses for custom validation.

        Args:
            **kwargs: Input parameters to validate

        Returns:
            Dict with validation errors (empty if valid)
        """
        return {}

    async def safe_execute(self, request_id: str = None, **kwargs) -> ToolResult:
        """
        Execute tool with error handling, timing, and retry logic.

        Args:
            request_id: Unique identifier for the request
            **kwargs: Tool parameters

        Returns:
            ToolResult with execution metadata
        """
        start_time = time.time()

        try:
            # Validate inputs
            validation_errors = self.validate_inputs(**kwargs)
            if validation_errors:
                return ToolResult.error(
                    error=f"Validation failed: {validation_errors}",
                    execution_time=time.time() - start_time,
                    tool_name=self.name,
                    request_id=request_id
                )

            # Execute with timeout and retry logic
            result = await self._execute_with_retries(
                request_id=request_id,
                **kwargs
            )

            # Add execution metadata
            result.execution_time = time.time() - start_time
            result.tool_name = self.name
            result.request_id = request_id

            return result

        except asyncio.TimeoutError:
            return ToolResult.error(
                error=f"Tool execution timed out after {self.timeout}s",
                execution_time=time.time() - start_time,
                tool_name=self.name,
                request_id=request_id,
                metadata={"timeout": self.timeout}
            )

        except Exception as e:
            logger.error(f"Unexpected error in {self.name}: {e}", exc_info=True)
            return ToolResult.error(
                error=f"Unexpected error: {str(e)}",
                execution_time=time.time() - start_time,
                tool_name=self.name,
                request_id=request_id,
                metadata={"error_type": type(e).__name__}
            )

    async def _execute_with_retries(self, request_id: str = None, **kwargs) -> ToolResult:
        """Execute with retry logic"""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    self.execute(**kwargs),
                    timeout=self.timeout
                )
                return result

            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"Tool {self.name} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                    )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

        # If we get here, all retries failed
        raise last_error

# ============================================================================
# 2. VALIDATION SCHEMAS
# ============================================================================

class StellarAddressSchema(BaseModel):
    """Stellar address validation schema"""
    address: str = Field(..., min_length=56, max_length=56)

    @validator('address')
    def validate_stellar_address(cls, v):
        if not v.startswith('G'):
            raise ValueError('Stellar address must start with G')
        if len(v) != 56:
            raise ValueError('Stellar address must be 56 characters')
        # Add more validation as needed
        return v.upper()

class AmountSchema(BaseModel):
    """Amount validation schema"""
    amount: str = Field(..., regex=r'^\d+(\.\d{1,7})?$')

    @validator('amount')
    def validate_amount(cls, v):
        try:
            amount = float(v)
            if amount <= 0:
                raise ValueError('Amount must be positive')
            if amount > 1000000:  # Reasonable limit
                raise ValueError('Amount exceeds maximum limit')
            return v
        except ValueError:
            raise ValueError('Invalid amount format')

class TransactionSchema(BaseModel):
    """Transaction validation schema"""
    source_account: StellarAddress
    destination_account: StellarAddress
    amount: AmountSchema
    asset_code: Optional[str] = Field(None, max_length=12)
    asset_issuer: Optional[StellarAddress] = None
    memo: Optional[str] = Field(None, max_length=28)

    @validator('memo')
    def validate_memo(cls, v):
        if v and len(v.encode('utf-8')) > 28:
            raise ValueError('Memo too long (max 28 bytes)')
        return v

# ============================================================================
# 3. EXAMPLE STANDARDIZED TOOLS
# ============================================================================

class StellarAccountTool(BaseTool):
    """Standardized Stellar account management tool"""

    def __init__(self):
        super().__init__()
        self.description = "Manage Stellar accounts: create, fund, check balance, list accounts"
        self.timeout = 60.0  # Account operations can be slower

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "action": {
                    "type": "string",
                    "enum": ["create", "list", "balance", "fund"],
                    "description": "Action to perform"
                },
                "address": {
                    "type": "string",
                    "optional": True,
                    "description": "Stellar address (required for balance/fund)"
                },
                "account_name": {
                    "type": "string",
                    "optional": True,
                    "description": "Name for new account (required for create)"
                }
            }
        }

    def validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate account tool inputs"""
        errors = {}
        action = kwargs.get("action")

        if not action:
            errors["action"] = "Action is required"

        if action in ["balance", "fund"] and not kwargs.get("address"):
            errors["address"] = f"Address is required for {action} action"

        if action == "create" and not kwargs.get("account_name"):
            errors["account_name"] = "Account name is required for create action"

        return errors

    async def execute(self, **kwargs) -> ToolResult:
        """Execute Stellar account operation"""
        action = kwargs["action"]

        try:
            if action == "create":
                return await self._create_account(kwargs.get("account_name"))
            elif action == "list":
                return await self._list_accounts()
            elif action == "balance":
                return await self._get_balance(kwargs["address"])
            elif action == "fund":
                return await self._fund_account(kwargs["address"])
            else:
                return ToolResult.error(f"Unknown action: {action}")

        except Exception as e:
            return ToolResult.error(f"Account operation failed: {str(e)}")

    async def _create_account(self, account_name: str) -> ToolResult:
        """Create new Stellar account"""
        # Import and use account management functions
        try:
            from tools.agent.account_management import create_agent_account

            result = create_agent_account(account_name)

            if result.get("success", True):
                return ToolResult.success(
                    data={
                        "address": result["address"],
                        "name": result["name"],
                        "network": result["network"],
                        "funded": result.get("funded", False)
                    }
                )
            else:
                return ToolResult.error(result.get("error", "Unknown error"))

        except ImportError:
            return ToolResult.error("Account management tools not available")
        except Exception as e:
            return ToolResult.error(f"Failed to create account: {str(e)}")

    async def _list_accounts(self) -> ToolResult:
        """List all agent accounts"""
        try:
            from tools.agent.account_management import list_agent_accounts

            accounts = list_agent_accounts()
            return ToolResult.success(data={"accounts": accounts})

        except ImportError:
            return ToolResult.error("Account management tools not available")
        except Exception as e:
            return ToolResult.error(f"Failed to list accounts: {str(e)}")

    async def _get_balance(self, address: str) -> ToolResult:
        """Get account balance"""
        try:
            # Validate address format
            schema = StellarAddressSchema(address=address)
            address = schema.address

            # Use Stellar SDK to get balance (MAINNET ONLY)
            from stellar_sdk.server import Server
            server = Server("https://horizon.stellar.org")

            account = server.load_account(address)
            balances = []

            for balance in account.balances:
                balances.append({
                    "asset_type": balance.asset_type,
                    "asset_code": getattr(balance, 'asset_code', 'XLM'),
                    "balance": balance.balance,
                    "limit": getattr(balance, 'limit', None)
                })

            return ToolResult.success(
                data={
                    "address": address,
                    "balances": balances
                }
            )

        except Exception as e:
            return ToolResult.error(f"Failed to get balance: {str(e)}")

    async def _fund_account(self, address: str) -> ToolResult:
        """Fund account using friendbot"""
        try:
            # Validate address format
            schema = StellarAddressSchema(address=address)
            address = schema.address

            import requests
            response = requests.post(
                f"https://friendbot.stellar.org?addr={address}"
            )

            if response.status_code == 200:
                return ToolResult.success(
                    data={
                        "address": address,
                        "funded": True,
                        "response": response.json()
                    }
                )
            else:
                return ToolResult.error(f"Friendbot funding failed: {response.text}")

        except Exception as e:
            return ToolResult.error(f"Failed to fund account: {str(e)}")

class StellarTradingTool(BaseTool):
    """Standardized Stellar trading tool"""

    def __init__(self):
        super().__init__()
        self.description = "Execute trades on Stellar DEX: create offers, manage orders, query orderbooks"
        self.timeout = 45.0

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "action": {
                    "type": "string",
                    "enum": ["create_offer", "manage_offer", "delete_offer", "orderbook", "offers"],
                    "description": "Trading action to perform"
                },
                "selling": {
                    "type": "string",
                    "description": "Asset being sold (e.g., 'XLM' or 'USD:issuer')"
                },
                "buying": {
                    "type": "string",
                    "description": "Asset being bought"
                },
                "amount": {
                    "type": "string",
                    "description": "Amount to trade"
                },
                "price": {
                    "type": "string",
                    "description": "Price per unit"
                },
                "offer_id": {
                    "type": "string",
                    "description": "Offer ID for manage/delete operations"
                }
            }
        }

    def validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate trading tool inputs"""
        errors = {}
        action = kwargs.get("action")

        if not action:
            errors["action"] = "Action is required"

        # Validate required parameters for different actions
        if action in ["create_offer", "manage_offer"]:
            for field in ["selling", "buying", "amount"]:
                if not kwargs.get(field):
                    errors[field] = f"{field} is required for {action}"

        if action in ["manage_offer", "delete_offer"] and not kwargs.get("offer_id"):
            errors["offer_id"] = f"offer_id is required for {action}"

        if action == "orderbook":
            if not kwargs.get("selling") or not kwargs.get("buying"):
                errors["trading_pair"] = "Both selling and buying required for orderbook"

        return errors

    async def execute(self, **kwargs) -> ToolResult:
        """Execute trading operation"""
        action = kwargs["action"]

        try:
            if action == "create_offer":
                return await self._create_offer(**kwargs)
            elif action == "manage_offer":
                return await self._manage_offer(**kwargs)
            elif action == "delete_offer":
                return await self._delete_offer(kwargs["offer_id"])
            elif action == "orderbook":
                return await self._get_orderbook(kwargs["selling"], kwargs["buying"])
            elif action == "offers":
                return await self._get_account_offers(kwargs.get("account_address"))
            else:
                return ToolResult.error(f"Unknown action: {action}")

        except Exception as e:
            return ToolResult.error(f"Trading operation failed: {str(e)}")

    async def _create_offer(self, **kwargs) -> ToolResult:
        """Create new trading offer"""
        # Implementation would use Stellar SDK to create offer
        return ToolResult.success(
            data={"message": "Offer creation not implemented yet", "action": "create_offer"}
        )

    async def _manage_offer(self, **kwargs) -> ToolResult:
        """Manage existing offer"""
        return ToolResult.success(
            data={"message": "Offer management not implemented yet", "action": "manage_offer"}
        )

    async def _delete_offer(self, offer_id: str) -> ToolResult:
        """Delete existing offer"""
        return ToolResult.success(
            data={"message": "Offer deletion not implemented yet", "action": "delete_offer"}
        )

    async def _get_orderbook(self, selling: str, buying: str) -> ToolResult:
        """Get orderbook for trading pair"""
        try:
            import requests
            from stellar_sdk import Asset

            # Parse assets
            if ":" in selling:
                selling_asset_code, selling_issuer = selling.split(":")
                selling_asset = Asset(selling_asset_code, selling_issuer)
            else:
                selling_asset = Asset.native()

            if ":" in buying:
                buying_asset_code, buying_issuer = buying.split(":")
                buying_asset = Asset(buying_asset_code, buying_issuer)
            else:
                buying_asset = Asset.native()

            # Query orderbook (MAINNET ONLY)
            server_url = "https://horizon.stellar.org"
            response = requests.get(
                f"{server_url}/order_book",
                params={
                    "selling_asset_type": selling_asset.type,
                    "selling_asset_code": getattr(selling_asset, 'code', None),
                    "selling_asset_issuer": getattr(selling_asset, 'issuer', None),
                    "buying_asset_type": buying_asset.type,
                    "buying_asset_code": getattr(buying_asset, 'code', None),
                    "buying_asset_issuer": getattr(buying_asset, 'issuer', None),
                    "limit": 20
                }
            )

            if response.status_code == 200:
                orderbook_data = response.json()
                return ToolResult.success(data={"orderbook": orderbook_data})
            else:
                return ToolResult.error(f"Failed to fetch orderbook: {response.text}")

        except Exception as e:
            return ToolResult.error(f"Failed to get orderbook: {str(e)}")

    async def _get_account_offers(self, account_address: str = None) -> ToolResult:
        """Get account offers"""
        if not account_address:
            return ToolResult.error("Account address required for offers query")

        try:
            import requests
            server_url = "https://horizon.stellar.org"  # MAINNET ONLY
            response = requests.get(f"{server_url}/accounts/{account_address}/offers")

            if response.status_code == 200:
                offers_data = response.json()
                return ToolResult.success(data={"offers": offers_data["_embedded"]["records"]})
            else:
                return ToolResult.error(f"Failed to fetch offers: {response.text}")

        except Exception as e:
            return ToolResult.error(f"Failed to get offers: {str(e)}")

# ============================================================================
# 4. TOOL REGISTRY AND FACTORY
# ============================================================================

class StandardizedToolRegistry:
    """Registry for managing standardized tools"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools"""
        self.register_tool("stellar_account", StellarAccountTool())
        self.register_tool("stellar_trading", StellarTradingTool())

    def register_tool(self, name: str, tool: BaseTool):
        """Register a tool"""
        self.tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return self.tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self.tools.values())

    def get_langchain_tools(self, user_context: Dict[str, Any] = None) -> List[Callable]:
        """Convert tools to LangChain format"""
        langchain_tools = []

        for tool_name, tool_instance in self.tools.items():
            langchain_tool = self._convert_to_langchain_format(
                tool_instance, tool_name, user_context
            )
            langchain_tools.append(langchain_tool)

        return langchain_tools

    def _convert_to_langchain_format(
        self,
        tool: BaseTool,
        tool_name: str,
        user_context: Dict[str, Any] = None
    ) -> Callable:
        """Convert standardized tool to LangChain format"""
        from langchain_core.tools import tool

        @tool(name=tool_name, description=tool.description)
        async def langchain_tool_wrapper(**kwargs):
            # Add user context to kwargs if provided
            if user_context:
                kwargs.update(user_context)

            # Generate request ID
            import uuid
            request_id = str(uuid.uuid4())

            # Execute tool with safety wrapper
            result = await tool.safe_execute(request_id=request_id, **kwargs)

            # Convert result to string for LangChain
            if result.status == ToolStatus.SUCCESS:
                if result.data:
                    return self._format_result_for_langchain(result.data)
                else:
                    return f"✅ {tool_name} completed successfully"
            else:
                return f"❌ {tool_name} failed: {result.error}"

        return langchain_tool_wrapper

    def _format_result_for_langchain(self, data: Dict[str, Any]) -> str:
        """Format tool result for LangChain consumption"""
        if isinstance(data, dict):
            formatted_parts = []
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    formatted_parts.append(f"{key}: {json.dumps(value, indent=2)}")
                else:
                    formatted_parts.append(f"{key}: {value}")
            return "\n".join(formatted_parts)
        else:
            return str(data)

# Global tool registry instance
tool_registry = StandardizedToolRegistry()

# ============================================================================
# 5. USAGE EXAMPLES
# ============================================================================

"""
# Example usage in agent core:

async def execute_tool_with_standardized_interface():
    # Get tool from registry
    account_tool = tool_registry.get_tool("stellar_account")

    # Execute with safety wrapper
    result = await account_tool.safe_execute(
        request_id="req_123",
        action="create",
        account_name="My Test Account"
    )

    if result.status == ToolStatus.SUCCESS:
        print(f"Account created: {result.data['address']}")
    else:
        print(f"Failed to create account: {result.error}")

# Example usage with LangChain integration:

def get_langchain_tools_for_agent(user_context):
    return tool_registry.get_langchain_tools(user_context)
"""

# ============================================================================
# 6. MIGRATION GUIDE
# ============================================================================

MIGRATION_GUIDE = """
# Tool Standardization Migration Guide

## Current State
- Mixed sync/async tool implementations
- Inconsistent error handling
- No standardized result format
- Complex tool execution logic in agent/core.py

## Target State
- All tools inherit from BaseTool
- Consistent async interface
- Standardized ToolResult format
- Built-in validation and error handling
- Automatic retry logic and timeouts

## Migration Steps

### Step 1: Identify Legacy Tools
```bash
find backend -name "*.py" -exec grep -l "@tool" {} \;
```

### Step 2: Create Standardized Versions
For each legacy tool:
1. Create new class inheriting from BaseTool
2. Move logic to async execute() method
3. Add validation schema
4. Add proper error handling
5. Test thoroughly

### Step 3: Update Tool Registry
1. Register new standardized tools
2. Remove old tool imports
3. Update agent core to use registry

### Step 4: Update LangChain Integration
1. Use tool_registry.get_langchain_tools()
2. Remove complex tool execution logic
3. Simplify agent/core.py significantly

### Step 5: Testing
1. Unit tests for each tool
2. Integration tests with agent
3. End-to-end tests for critical flows

## Benefits
- Consistent error handling across all tools
- Built-in validation prevents bad inputs
- Automatic retry logic improves reliability
- Standardized monitoring and logging
- Easier to add new tools
- Simplified agent core logic
"""