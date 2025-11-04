#!/usr/bin/env python3
"""
Test DeFindex tool imports
"""

def test_imports():
    print("Testing DeFindex tool imports...")

    try:
        from defindex_tools import discover_high_yield_vaults, get_defindex_vault_details, prepare_defindex_deposit
        print("✅ Import successful")

        print(f"discover_high_yield_vaults: {discover_high_yield_vaults}")
        print(f"get_defindex_vault_details: {get_defindex_vault_details}")
        print(f"prepare_defindex_deposit: {prepare_defindex_deposit}")

        # Check if they are callable
        print(f"discover_high_yield_vaults is callable: {callable(discover_high_yield_vaults)}")
        print(f"get_defindex_vault_details is callable: {callable(get_defindex_vault_details)}")
        print(f"prepare_defindex_deposit is callable: {callable(prepare_defindex_deposit)}")

        # Check tool attributes
        if hasattr(discover_high_yield_vaults, 'name'):
            print(f"discover_high_yield_vaults.name: {discover_high_yield_vaults.name}")
        if hasattr(discover_high_yield_vaults, 'description'):
            print(f"discover_high_yield_vaults.description: {discover_high_yield_vaults.description[:100]}...")

    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()