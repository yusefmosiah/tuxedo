#!/usr/bin/env python3
"""
Test both sync and async tool approaches
"""

import asyncio
from typing import Optional
from langchain_core.tools import tool
from defindex_soroban import get_defindex_soroban

# Option 1: Sync tool (current fix)
@tool
def discover_high_yield_vaults_sync(min_apy: Optional[float] = 15.0) -> str:
    """Discover DeFindex vaults with high yields using enhanced data sources (sync version)."""
    try:
        # Run the async function inside sync tool
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_get_vault_data_sync(min_apy))
        loop.close()
        return result
    except Exception as e:
        return f"Error: {str(e)}"

async def _get_vault_data_sync(min_apy: float) -> str:
    """Helper async function for sync version"""
    defindex = get_defindex_soroban('mainnet')
    vaults_data = await defindex.get_available_vaults(min_apy=min_apy)

    if not vaults_data:
        return f"No vaults found with APY above {min_apy}%."

    result = f"Found {len(vaults_data)} high-yield DeFindex vaults on Stellar:\n\n"
    for i, v in enumerate(vaults_data[:8], 1):
        risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}.get(v.get('risk_level', 'Medium'), '⚪')
        result += f"{i}. {v['name']} ({v['symbol']}) {risk_emoji}\n"
        result += f"   APY: {v['apy']:.1f}% | Strategy: {v.get('strategy', 'Unknown')}\n"
        result += f"   TVL: ${v['tvl']:,.0f} | Type: {v.get('asset_type', 'Unknown')}\n"
        result += f"   Address: {v['address']}\n\n"

    result += "💡 **Risk Guide**: 🟢 Low Risk (Stablecoins) | 🟡 Medium Risk (XLM) | 🔴 High Risk (Alt tokens)\n"
    result += "📊 Data includes realistic market-based APY and TVL calculations.\n"
    result += "🧪 For testing, I can prepare demo transactions on testnet using these mainnet vault references."
    return result

# Option 2: Pure async tool (original approach)
@tool
async def discover_high_yield_vaults_async(min_apy: Optional[float] = 15.0) -> str:
    """Discover DeFindex vaults with high yields using enhanced data sources (async version)."""
    try:
        defindex = get_defindex_soroban('mainnet')
        vaults_data = await defindex.get_available_vaults(min_apy=min_apy)

        if not vaults_data:
            return f"No vaults found with APY above {min_apy}%."

        result = f"Found {len(vaults_data)} high-yield DeFindex vaults on Stellar:\n\n"
        for i, v in enumerate(vaults_data[:8], 1):
            risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}.get(v.get('risk_level', 'Medium'), '⚪')
            result += f"{i}. {v['name']} ({v['symbol']}) {risk_emoji}\n"
            result += f"   APY: {v['apy']:.1f}% | Strategy: {v.get('strategy', 'Unknown')}\n"
            result += f"   TVL: ${v['tvl']:,.0f} | Type: {v.get('asset_type', 'Unknown')}\n"
            result += f"   Address: {v['address']}\n\n"

        result += "💡 **Risk Guide**: 🟢 Low Risk (Stablecoins) | 🟡 Medium Risk (XLM) | 🔴 High Risk (Alt tokens)\n"
        result += "📊 Data includes realistic market-based APY and TVL calculations.\n"
        result += "🧪 For testing, I can prepare demo transactions on testnet using these mainnet vault references."
        return result

    except Exception as e:
        return f"Error: {str(e)}"

def test_both_approaches():
    print("Testing both sync and async tool approaches...")

    print(f"Sync tool: {discover_high_yield_vaults_sync}")
    print(f"  - Type: {type(discover_high_yield_vaults_sync)}")
    print(f"  - Callable: {callable(discover_high_yield_vaults_sync)}")
    print(f"  - Name: {getattr(discover_high_yield_vaults_sync, 'name', 'NO_NAME')}")

    print(f"\nAsync tool: {discover_high_yield_vaults_async}")
    print(f"  - Type: {type(discover_high_yield_vaults_async)}")
    print(f"  - Callable: {callable(discover_high_yield_vaults_async)}")
    print(f"  - Name: {getattr(discover_high_yield_vaults_async, 'name', 'NO_NAME')}")

    # Test sync execution
    try:
        print(f"\nTesting sync execution...")
        result = discover_high_yield_vaults_sync.invoke({"min_apy": 25.0})
        print(f"✅ Sync tool executed successfully: {len(result)} chars")
    except Exception as e:
        print(f"❌ Sync tool failed: {e}")

    # Test async execution
    try:
        print(f"\nTesting async execution...")
        result = asyncio.run(discover_high_yield_vaults_async.ainvoke({"min_apy": 25.0}))
        print(f"✅ Async tool executed successfully: {len(result)} chars")
    except Exception as e:
        print(f"❌ Async tool failed: {e}")

if __name__ == "__main__":
    test_both_approaches()