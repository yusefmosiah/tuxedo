"""
Vault Tools - LangChain tool wrappers for TuxedoVault
AI agent tools for vault deposit, withdrawal, and performance tracking
"""

from typing import Optional
from langchain_core.tools import tool
from vault_manager import get_vault_manager

# Asset addresses on Stellar mainnet
ASSET_ADDRESSES = {
    "USDC": "CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC",  # Example USDC address
    # Add more assets as needed
}


@tool
async def deposit_to_vault(amount: float, asset: str = "USDC") -> str:
    """
    Deposit assets to the TuxedoVault and receive TUX0 shares.
    The vault uses your deposited funds to earn yield through Blend Capital pools.

    Args:
        amount: Amount to deposit (e.g., 100.0 for 100 USDC)
        asset: Asset to deposit (default: USDC)

    Returns:
        Status message with number of shares minted

    Example:
        "Deposited 100 USDC. You received 100.0000000 TUX0 shares."
    """
    vault = get_vault_manager()
    if not vault:
        return "Error: Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables."

    # Convert amount to 7 decimals (Stellar standard)
    amount_stroops = int(amount * 10**7)

    # Get asset address
    if asset not in ASSET_ADDRESSES:
        return f"Error: Asset {asset} not supported. Supported assets: {', '.join(ASSET_ADDRESSES.keys())}"

    asset_address = ASSET_ADDRESSES[asset]

    # Note: In production, this would need user authorization
    # For now, return instructions for user to complete deposit
    result = await vault.deposit_to_vault(
        user_address="",  # Would be provided by connected wallet
        amount=amount_stroops,
        user_keypair=None,  # User signs via wallet
    )

    if result["status"] == "success":
        shares = amount  # Simplified - actual shares from transaction result
        return f"Deposited {amount} {asset}. You received {shares} TUX0 shares. Your funds are now earning yield in the vault!"
    elif result["status"] == "needs_signature":
        return f"Deposit transaction prepared for {amount} {asset}. Please sign the transaction in your wallet to complete the deposit."
    else:
        return f"Error depositing to vault: {result['message']}"


@tool
async def withdraw_from_vault(shares: float) -> str:
    """
    Withdraw assets from TuxedoVault by burning TUX0 shares.
    You'll receive USDC proportional to your share of the vault.

    Args:
        shares: Number of TUX0 shares to burn (e.g., 50.0)

    Returns:
        Status message with amount of assets withdrawn

    Example:
        "Withdrew 98.5 USDC by burning 50.0 TUX0 shares."
    """
    vault = get_vault_manager()
    if not vault:
        return "Error: Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables."

    # Convert shares to 7 decimals
    shares_stroops = int(shares * 10**7)

    result = await vault.withdraw_from_vault(
        user_address="",  # Would be provided by connected wallet
        shares=shares_stroops,
        user_keypair=None,  # User signs via wallet
    )

    if result["status"] == "success":
        amount = shares  # Simplified - actual amount from transaction result
        return f"Withdrew {amount} USDC by burning {shares} TUX0 shares. Funds transferred to your wallet!"
    elif result["status"] == "needs_signature":
        return f"Withdrawal transaction prepared for {shares} TUX0 shares. Please sign the transaction in your wallet."
    else:
        return f"Error withdrawing from vault: {result['message']}"


@tool
async def get_vault_performance() -> str:
    """
    Get current TuxedoVault performance metrics.
    Shows TVL, share value, and estimated APY.

    Returns:
        Formatted vault performance data

    Example:
        "TUX0 Vault Performance:
        - TVL: $10,543.21
        - Share Value: $1.0234
        - Current APY: 8.45%"
    """
    vault = get_vault_manager()
    if not vault:
        return "Error: Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables."

    stats = await vault.get_vault_stats()

    if stats["status"] == "error":
        return f"Error fetching vault performance: {stats['message']}"

    tvl = stats.get("tvl", 0) / 1e7
    share_value = stats.get("share_value", 1.0) / 1e7
    total_shares = stats.get("total_shares", 0) / 1e7
    initial_deposits = stats.get("initial_deposits", 0) / 1e7

    # Calculate APY
    apy = vault.calculate_apy(
        int(initial_deposits * 1e7), int(tvl * 1e7), days=30
    )

    return f"""TUX0 Vault Performance:
- TVL: ${tvl:,.2f} USDC
- Share Value: ${share_value:.7f}
- Total Shares: {total_shares:,.2f} TUX0
- Current APY: {apy:.2f}%
- Fee Structure: 2% platform fee, 98% to users

💡 Your TUX0 shares automatically earn yield from Blend Capital pools!"""


@tool
async def get_my_vault_position(user_address: str) -> str:
    """
    Get your current position in the TuxedoVault.
    Shows your share balance and current value.

    Args:
        user_address: Your Stellar address

    Returns:
        Your vault position details

    Example:
        "Your Vault Position:
        - TUX0 Shares: 100.0000000
        - Current Value: $102.34
        - Yield Earned: $2.34 (2.34%)"
    """
    vault = get_vault_manager()
    if not vault:
        return "Error: Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables."

    # Get user shares
    shares_result = await vault.get_user_shares(user_address)

    if shares_result["status"] == "error":
        return f"Error fetching vault position: {shares_result['message']}"

    user_shares = shares_result.get("shares", 0) / 1e7

    # Get vault stats for share value
    stats = await vault.get_vault_stats()
    share_value = stats.get("share_value", 1.0) / 1e7

    # Calculate position value
    position_value = user_shares * share_value

    # Calculate yield (assuming initial deposit was 1:1)
    initial_value = user_shares * 1.0
    yield_earned = position_value - initial_value
    yield_percent = (yield_earned / initial_value * 100) if initial_value > 0 else 0

    return f"""Your Vault Position:
- TUX0 Shares: {user_shares:.7f}
- Current Value: ${position_value:.2f}
- Yield Earned: ${yield_earned:.2f} ({yield_percent:.2f}%)

🎩 Keep holding to earn more yield from Blend Capital!"""


@tool
async def vault_agent_supply_to_blend(
    pool_name: str, asset: str = "USDC", amount: float = 0
) -> str:
    """
    Agent supplies vault funds to a Blend Capital pool to earn yield.
    This is an autonomous operation - the agent manages the strategy.

    Args:
        pool_name: Blend pool name ("comet", "fixed", or "yieldblox")
        asset: Asset to supply (default: USDC)
        amount: Amount to supply (if 0, agent decides optimal amount)

    Returns:
        Status message

    Example:
        "Agent supplied 5,000 USDC to Comet pool. Now earning 8.2% APY."
    """
    vault = get_vault_manager()
    if not vault:
        return "Error: Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables."

    # Blend pool addresses on mainnet
    BLEND_POOLS = {
        "comet": "CCSHXLJJDGU5PY6JE4X4VLZBQMTR3J7CRLCMPHW3O5D2BDQPCDH4MCCP",  # Example
        "fixed": "CCSHXLJJDGU5PY6JE4X4VLZBQMTR3J7CRLCMPHW3O5D2BDQPCDH4MCCF",  # Example
        "yieldblox": "CCSHXLJJDGU5PY6JE4X4VLZBQMTR3J7CRLCMPHW3O5D2BDQPCDH4MCCY",  # Example
    }

    if pool_name.lower() not in BLEND_POOLS:
        return f"Error: Pool {pool_name} not supported. Available pools: comet, fixed, yieldblox"

    pool_address = BLEND_POOLS[pool_name.lower()]
    asset_address = ASSET_ADDRESSES.get(asset)

    if not asset_address:
        return f"Error: Asset {asset} not supported."

    # If amount is 0, use 50% of vault TVL (simple strategy)
    if amount == 0:
        stats = await vault.get_vault_stats()
        tvl = stats.get("tvl", 0) / 1e7
        amount = tvl * 0.5  # Supply 50% of vault

    amount_stroops = int(amount * 10**7)

    # Execute agent strategy
    result = await vault.agent_execute_strategy(
        strategy="supply", pool=pool_address, asset=asset_address, amount=amount_stroops
    )

    if result["status"] == "success":
        return f"✅ Agent supplied {amount:.2f} {asset} to {pool_name.capitalize()} pool. Vault is now earning yield! Transaction: {result['tx_hash'][:8]}..."
    else:
        return f"Error executing strategy: {result['message']}"


@tool
async def vault_agent_withdraw_from_blend(
    pool_name: str, asset: str = "USDC", amount: float = 0
) -> str:
    """
    Agent withdraws funds from a Blend Capital pool back to vault.
    Used for rebalancing or responding to opportunities.

    Args:
        pool_name: Blend pool name ("comet", "fixed", or "yieldblox")
        asset: Asset to withdraw (default: USDC)
        amount: Amount to withdraw

    Returns:
        Status message

    Example:
        "Agent withdrew 2,500 USDC from Fixed pool back to vault."
    """
    vault = get_vault_manager()
    if not vault:
        return "Error: Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables."

    BLEND_POOLS = {
        "comet": "CCSHXLJJDGU5PY6JE4X4VLZBQMTR3J7CRLCMPHW3O5D2BDQPCDH4MCCP",  # Example
        "fixed": "CCSHXLJJDGU5PY6JE4X4VLZBQMTR3J7CRLCMPHW3O5D2BDQPCDH4MCCF",  # Example
        "yieldblox": "CCSHXLJJDGU5PY6JE4X4VLZBQMTR3J7CRLCMPHW3O5D2BDQPCDH4MCCY",  # Example
    }

    if pool_name.lower() not in BLEND_POOLS:
        return f"Error: Pool {pool_name} not supported. Available pools: comet, fixed, yieldblox"

    pool_address = BLEND_POOLS[pool_name.lower()]
    asset_address = ASSET_ADDRESSES.get(asset)

    if not asset_address:
        return f"Error: Asset {asset} not supported."

    amount_stroops = int(amount * 10**7)

    # Execute withdraw strategy
    result = await vault.agent_execute_strategy(
        strategy="withdraw",
        pool=pool_address,
        asset=asset_address,
        amount=amount_stroops,
    )

    if result["status"] == "success":
        return f"✅ Agent withdrew {amount:.2f} {asset} from {pool_name.capitalize()} pool. Funds back in vault. Transaction: {result['tx_hash'][:8]}..."
    else:
        return f"Error executing strategy: {result['message']}"


@tool
async def vault_distribute_yield() -> str:
    """
    Distribute accumulated yield in the vault.
    Anyone can call this function.
    Fee structure: 98% stays with users, 2% to platform.

    Returns:
        Status message

    Example:
        "Yield distributed! Platform received $20.00 (2%), users kept $980.00 (98%)"
    """
    vault = get_vault_manager()
    if not vault:
        return "Error: Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables."

    # Use agent keypair to call distribute_yield
    result = await vault.distribute_yield(vault.agent)

    if result["status"] == "success":
        return f"✅ Yield distribution completed! Transaction: {result['tx_hash'][:8]}... Fee structure: 2% platform, 98% to users."
    else:
        return f"Error distributing yield: {result['message']}"


# Export all vault tools
VAULT_TOOLS = [
    deposit_to_vault,
    withdraw_from_vault,
    get_vault_performance,
    get_my_vault_position,
    vault_agent_supply_to_blend,
    vault_agent_withdraw_from_blend,
    vault_distribute_yield,
]
