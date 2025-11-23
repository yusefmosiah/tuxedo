# Tuxedo Codebase Cleanup Report
**Comprehensive Code, Test, and Documentation Review**

**Date**: 2025-11-23
**Context**: Transitioning from Stellar hackathon project to multichain Choir/Ghostwriter platform
**Objective**: Identify and purge/update out-of-date tests and documentation before continuing development

---

## Executive Summary

### Current State
- **Vision Shift**: Stellar-only DeFi agent (hackathon) → Multichain Choir/Ghostwriter platform (learning economy)
- **New Feature**: Ghostwriter fully implemented (~2000+ lines, 8-stage research pipeline)
- **Legacy Code**: Significant Stellar/Blend/DeFindex code from hackathon phase
- **Documentation**: Mix of outdated hackathon docs and current multichain vision docs

### Key Findings
- **51 test files** reviewed (5 Ghostwriter, 14 Stellar legacy, 11 agent/chat, 24 sandbox)
- **45 documentation files** reviewed (many outdated from hackathon phase)
- **CLAUDE.md is outdated** - still heavily Stellar-focused, contradicts MULTICHAIN_EVM_MIGRATION_PLAN.md
- **Sandbox directory** contains 24 experimental test files that should be purged
- **Implementation files** are clean - main codebase is well-structured

### Recommendations Summary
- **PURGE**: 38 test files (24 sandbox + 14 Stellar legacy)
- **PURGE**: 29 documentation files (outdated hackathon docs)
- **UPDATE**: CLAUDE.md to reflect current Choir/Ghostwriter multichain vision
- **UPDATE**: 11 agent/chat tests to be chain-agnostic
- **KEEP**: 5 Ghostwriter tests, 16 current docs, all implementation code

---

## Test Files Review

### Category 1: Ghostwriter Tests ✅ KEEP (5 files)
**Status**: Recently added, actively maintained, core feature

| File | Purpose | Status |
|------|---------|--------|
| `backend/test_ghostwriter.py` | Main pipeline test | ✅ Keep |
| `backend/test_ghostwriter_pipeline.py` | Alternative pipeline test | ✅ Keep (verify not duplicate) |
| `backend/test_websearch.py` | Tavily websearch integration | ✅ Keep |
| `backend/tests/test_ghostwriter_tool.py` | Tool wrapper test | ✅ Keep |
| `backend/tests/manual_test_verification.py` | Manual verification testing | ✅ Keep |

**Action**: Keep all, ensure no duplication between `test_ghostwriter.py` and `test_ghostwriter_pipeline.py`

---

### Category 2: Stellar Legacy Tests ❌ PURGE (14 files)
**Status**: Hackathon-era tests for Blend Capital v1/v2 pool queries, Soroswap, DeFindex

These tests were debugging tools during hackathon development. They reference:
- Specific Stellar mainnet pool contracts
- Blend Capital protocol (Stellar-only)
- Soroswap integration (Stellar DEX)
- Storage key queries and ledger entries (Stellar-specific debugging)

| File | Purpose | Why Purge |
|------|---------|-----------|
| `backend/test_blend_v2.py` | Blend v2 pool testing | Stellar-only, superseded by multichain |
| `backend/test_blend_query_fix.py` | Debug Blend queries | One-off debugging script |
| `backend/test_v2_debug.py` | V2 implementation debugging | One-off debugging script |
| `backend/test_v2_direct.py` | Direct V2 testing | Duplicate debugging effort |
| `backend/test_current_pools.py` | Query mainnet pools | Hardcoded Stellar contracts |
| `backend/test_confirmed_v2_pools.py` | Confirm pool addresses | One-off validation |
| `backend/test_blnd_emissions.py` | BLND token emissions | Blend-specific (Stellar) |
| `backend/test_storage_keys.py` | Soroban storage debugging | Low-level Stellar debugging |
| `backend/test_backstop.py` | Blend backstop module | Blend-specific (Stellar) |
| `backend/test_contract_info.py` | Contract metadata queries | General debugging |
| `backend/test_contract_methods.py` | Contract method inspection | General debugging |
| `backend/test_ledger_entries_simple.py` | Ledger entry queries | Stellar-specific |
| `backend/test_soroswap_integration.py` | Soroswap DEX integration | Stellar-only DEX |
| `backend/test_with_agent_account.py` | Agent account testing | Likely superseded |

**Action**: Delete all 14 files. If Blend/Soroswap integration is ever needed, refer to git history.

**Rationale**:
- Multichain pivot makes Stellar-specific tests obsolete
- These were debugging tools, not systematic test suites
- Implementation code (`blend_pool_tools.py`, `stellar_tools.py`) still exists for reference
- Can be recovered from git if needed

---

### Category 3: Agent/Chat Tests 🔄 UPDATE (11 files)
**Status**: Core functionality tests that should remain, but need updates for multichain

| File | Purpose | Required Update |
|------|---------|-----------------|
| `backend/tests/test_agent.py` | Basic agent functionality | Update to be chain-agnostic |
| `backend/tests/test_tools/test_agent_with_tools.py` | Agent tool calling | Remove Stellar-specific assertions |
| `backend/tests/test_agent_integration.py` | End-to-end agent test | Make chain-configurable |
| `backend/tests/test_agent_secret.py` | AGENT_STELLAR_SECRET import | Rename to test_agent_key_import.py |
| `backend/tests/test_agent_wallet.py` | Agent wallet management | Update for EVM accounts |
| `backend/tests/test_get_agent_account.py` | Agent account retrieval | Chain-agnostic updates |
| `backend/tests/test_agent_selection.py` | Agent selection logic | Verify still relevant |
| `backend/tests/test_agent_management/test_wallet_fix.py` | Wallet fix validation | Update or remove |
| `backend/tests/test_chat/test_multiturn.py` | Multi-turn conversations | ✅ Should work as-is |
| `backend/tests/test_chat/test_multiturn_with_tools.py` | Multi-turn with tools | Update tool examples |
| `backend/tests/test_blend_transaction_simulation.py` | Transaction simulation | Remove (Blend-specific) or generalize |

**Action**: Review each file to:
1. Remove hardcoded Stellar addresses/contracts
2. Make chain selection configurable (env var or parameter)
3. Update assertions to be protocol-agnostic
4. Rename files with "STELLAR" in the name
5. Consider deleting `test_blend_transaction_simulation.py` unless generalizable

**Notes**:
- `test_agent.py` and `test_agent_with_tools.py` reference Stellar network status queries
- Need to update to test with mock chain or configurable chain parameter
- Chat tests should work as-is since they're mostly about conversation flow

---

### Category 4: Sandbox Tests ❌ PURGE ALL (24 files)
**Status**: Experimental one-off tests from development phase

The `/sandbox/` directory contains experimental tests created during development. These were never meant to be permanent test suite components.

**Blend Integration Tests** (3 files):
- `test_blend_integration.py` - Stellar Blend protocol
- `test_mainnet_blend.py` - Mainnet Blend testing
- `test_mainnet_pool_discovery.py` - Pool discovery

**Vault/DeFindex Tests** (8 files):
- `test_deposit_to_vault.py` - References testnet vault that doesn't exist
- `test_withdraw_from_vault.py` - References testnet vault
- `simple_vault_test.py` - Simple deployment test
- `test_vault_deployment.py` - Deployment script
- `working_deposit_test.py` - Working version of deposit test
- `run_complete_vault_test.py` - Complete vault test runner
- `simple_deposit_test.py` - Simple deposit test
- Vault contract: `backend/vault_manager.py` references vault that was never deployed

**Payment/Transaction Tests** (5 files):
- `test_simple_manual_payment.py`
- `test_send_payment.py`
- `test_manual_payment_working.py`
- `test_comprehensive_manual_payment.py`
- `test_direct_soroban.py`

**Miscellaneous** (8 files):
- `test_user_isolation.py` - User isolation testing
- `test_agent_tools_loading.py` - Tool loading verification
- `test_comprehensive.py` - Comprehensive test suite
- `test_tool_schemas.py` - Tool schema validation
- `test_system_prompt.py` - System prompt testing
- `test_fix.py` - Generic fix testing
- `test_agent_account_import.py` - Account import
- `test_mainnet.py` - General mainnet testing
- `test_improved_error_handling.py` - Error handling

**Action**: Delete entire `/sandbox/` directory

**Rationale**:
- These are not systematic tests - they're development experiments
- Many reference contracts/deployments that don't exist
- Multiple versions of the same test (e.g., 4 different payment tests)
- If functionality is important, it should be in proper test suite
- Clutters the repository and creates confusion

---

## Documentation Review

### Category 1: Ghostwriter Documentation ✅ KEEP (6 files)

| File | Status | Notes |
|------|--------|-------|
| `backend/agent/ghostwriter/IMPLEMENTATION_SUMMARY.md` | ✅ Keep | Current implementation status |
| `backend/agent/ghostwriter/OPENHANDS_SDK_BEDROCK_CONFIGURATION.md` | ✅ Keep | AWS Bedrock setup |
| `backend/agent/ghostwriter/WEBSEARCH_SETUP.md` | ✅ Keep | Tavily integration |
| `docs/GHOSTWRITER_ARCHITECTURE_OPENHANDS_SDK.md` | ✅ Keep | Architecture doc |
| `docs/GHOSTWRITER_ARCHITECTURE_PRACTICAL.md` | ✅ Keep | Practical guide |
| `docs/GHOSTWRITER_PIPELINE_REDESIGN.md` | ✅ Keep | Pipeline design |

---

### Category 2: Current Vision Documentation ✅ KEEP (10 files)

| File | Status | Notes |
|------|--------|-------|
| `README.md` | ✅ Keep | Current project overview (Choir) |
| `UNIFIED_VISION.md` | ✅ Keep | Core vision document |
| `STYLEGUIDE.md` | ✅ Keep | Style guide |
| `docs/CHOIR_WHITEPAPER.md` | ✅ Keep | Whitepaper |
| `docs/MULTICHAIN_EVM_MIGRATION_PLAN.md` | ✅ Keep | Migration plan to Base/EVM |
| `docs/AWS_BEDROCK_CONFIGURATION.md` | ✅ Keep | AWS setup |
| `docs/AGENT_SDK_RESEARCH_AND_RECOMMENDATIONS.md` | ✅ Keep | Agent SDK research |
| `docs/CLAUDE_SDK_INTEGRATION.md` | ✅ Keep | Claude SDK docs |
| `docs/PASSKEY_ARCHITECTURE_V2.md` | ✅ Keep | Passkey system (chain-agnostic) |
| `docs/PASSKEY_IMPLEMENTATION_SUMMARY.md` | ✅ Keep | Passkey implementation |

---

### Category 3: Root-Level Docs 🔄 REVIEW (8 files)

| File | Status | Recommendation |
|------|--------|----------------|
| `CLAUDE.md` | ❌ **NEEDS MAJOR UPDATE** | Contradicts multichain vision |
| `SECURITY.md` | ✅ Keep | General security guidelines |
| `TESTING_STRATEGY.md` | 🔄 Review | May be outdated |
| `WEBSEARCH_IMPLEMENTATION_SUMMARY.md` | ✅ Keep | Ghostwriter websearch |
| `GHOSTWRITER_PIPELINE_TEST_RESULTS.md` | ✅ Keep | Test results |
| Root AWS/Bedrock docs (3 files) | ✅ Keep | Current setup docs |

**CLAUDE.md Critical Issues**:
- Lines 1-100: States "This system operates exclusively on mainnet with a non-custodial vault model"
- References TUX0 vault extensively (not deployed, Stellar-specific)
- References 19 Stellar/Blend tools as if they're the current implementation
- No mention of Choir, Ghostwriter, or multichain vision
- Contradicts `MULTICHAIN_EVM_MIGRATION_PLAN.md` which is the actual roadmap

**Recommendation**: Rewrite CLAUDE.md to reflect:
- Choir/Ghostwriter as the core product
- Multichain as the architecture direction
- Ghostwriter tools as primary functionality
- Optional DeFi as future feature (not current implementation)
- Passkey auth as proven working system

---

### Category 4: Hackathon/Outdated Docs ❌ PURGE (29 files)

**Stellar-Specific Implementation Docs** (13 files):
```
❌ docs/STELLAR_TOOLS_LANGCHAIN_FIX.md
❌ docs/STELLAR_WALLETS_KIT_INTEGRATION.md
❌ docs/STELLAR_WALLETS_KIT_PROGRESS.md
❌ docs/BLEND_YIELD_FARMING_IMPLEMENTATION_PLAN.md
❌ docs/blend_query_toolkit.md
❌ docs/DEFINDEX_API_NETWORK_PARAMETER_FIX.md
❌ docs/DEFINDEX_COMPREHENSIVE_GUIDE.md
❌ backend/BLEND_V2_IMPLEMENTATION_SUCCESS.md
❌ backend/BLND_EMISSIONS_IMPLEMENTATION_STATUS.md
❌ backend/BLEND_V1_VS_V2_FINDING.md
❌ backend/BLEND_QUERY_COMPLETE_SOLUTION.md
❌ backend/BLEND_QUERY_FIX.md
❌ backend/SOROSWAP_INTEGRATION_COMPLETE.md
```

**Vault/DeFindex Hackathon Docs** (9 files):
```
❌ docs/VAULT_IMPLEMENTATION_COMPLETE.md - Claims vault is complete (not deployed)
❌ docs/VAULT_DEPLOYMENT_COMPLETE.md - Vault not actually deployed
❌ docs/VAULT_DEPLOYMENT_GUIDE.md - Stellar-specific deployment
❌ docs/VAULT_IMPLEMENTATION_PLAN.md - Superseded by multichain plan
❌ docs/VAULT_COLLATERAL_ARCHITECTURE.md - Stellar-specific
❌ docs/DEPLOYED_TESTNET_INFRASTRUCTURE.md - References deployments that don't exist
❌ docs/DEPLOYMENT_FINAL_SUMMARY.md - Outdated
❌ docs/DEPLOYMENT_SUCCESS_REPORT.md - Outdated
❌ docs/STRATEGY_DEPLOYMENT_SUMMARY.md - DeFindex strategies (Stellar)
```

**Root-Level Hackathon Docs** (7 files):
```
❌ VAULT_MVP_SUMMARY.md - Stellar vault MVP
❌ SOROSWAP_IMPLEMENTATION_SUMMARY.md - Stellar DEX integration
❌ BLEND_QUERY_TESTING_REPORT.md - Blend protocol testing
❌ LAYER_2_TESTING_PROGRESS.md - Old testing progress
❌ LAYER_2_TESTING_PROGRESS_REPORT.md - Duplicate
❌ backend/LAYER2_TESTING_SESSION_REPORT.md - Old testing session
❌ tux0_vault_implementation_progress.md - Stellar vault progress
```

**Rationale for Purge**:
- Document features that were planned but never deployed (vaults, DeFindex)
- Reference Stellar-only architecture that's being deprecated
- Create confusion about current state ("deployment complete" when nothing deployed)
- Superseded by MULTICHAIN_EVM_MIGRATION_PLAN.md

**Action**: Delete all 29 files, keep git history for reference

---

### Category 5: Agent/Migration Docs 🔄 REVIEW (7 files)

| File | Status | Recommendation |
|------|--------|----------------|
| `docs/AGENT_MIGRATION_QUANTUM_LEAP.md` | 🔄 Review | Check if "Quantum Leap" is current |
| `docs/QUANTUM_LEAP_PROGRESS.md` | 🔄 Review | Merge with above or delete |
| `docs/AGENT_ACCOUNT_SECURITY_PLAN.md` | 🔄 Review | Verify still relevant |
| `docs/ACCOUNT_SECURITY_MODEL.md` | 🔄 Review | Merge duplicates |
| `docs/security_action_plan.md` | 🔄 Review | Check if actioned |
| `docs/security_improvements.md` | 🔄 Review | Merge into one security doc |
| `docs/AGENT_FILESYSTEM_ISOLATION.md` | ✅ Keep | Relevant for multichain |

**Action**: Review these 7 files to:
1. Merge duplicate security docs into single source of truth
2. Verify "Quantum Leap" terminology is still used
3. Delete if superseded by implemented features

---

### Category 6: Miscellaneous Docs 🔄 REVIEW (7 files)

| File | Status | Recommendation |
|------|--------|----------------|
| `docs/AGENTIC_TRANSACTION_IMPLEMENTATION.md` | 🔄 Review | Check if implemented |
| `docs/WALLET_INTEGRATION_PLAN.md` | 🔄 Review | Plan vs actual implementation |
| `docs/MAINNET_INTEGRATION_PLAN.md` | ❌ Delete | Stellar mainnet plan (superseded) |
| `docs/PHALA_DEPLOYMENT_CHECKLIST.md` | 🔄 Review | Phala TEE deployment plan |
| `docs/ENVIRONMENT_SETUP.md` | ✅ Keep | General setup guide |
| `docs/creative_vault_strategy_design.md` | ❌ Delete | Stellar vault strategies |
| `docs/playful_path_to_vaults.md` | ❌ Delete | Stellar vault narrative doc |

---

## Implementation Code Review

### Core Implementation Files ✅ STATUS: CLEAN

**No changes recommended to implementation code**. The codebase is well-structured:

**Working Components**:
- ✅ `backend/agent/core.py` (784 lines) - LangChain agent orchestration
- ✅ `backend/agent/tool_factory.py` (1074 lines) - Per-request tool creation
- ✅ `backend/agent/ghostwriter/` - Complete Ghostwriter implementation (~2000 lines)
- ✅ `backend/account_manager.py` - Multi-user account management (chain-configurable)
- ✅ `backend/database_passkeys.py` - Passkey authentication (chain-agnostic)
- ✅ `backend/app.py` - FastAPI application factory

**Stellar Legacy Code** (Keep for now, deprecate with multichain):
- `backend/stellar_tools.py` (1225 lines) - Stellar tools implementation
- `backend/blend_pool_tools.py` - Blend Capital integration
- `backend/vault_tools.py` (383 lines) - Vault tools (references undeployed contracts)
- `backend/vault_manager.py` (404 lines) - Vault contract interface (never deployed)

**Why Keep Stellar Code**:
- Still functional and doesn't break anything
- Provides reference for future EVM tool implementation
- Can coexist with multichain until EVM tools are ready
- Documented as legacy in MULTICHAIN_EVM_MIGRATION_PLAN.md

**Frontend Implementation** ✅ STATUS: CLEAN
- No immediate changes needed
- Will require updates when EVM integration begins (Phase 5 of migration plan)
- Current Stellar wallet integration can coexist with new EVM wallets

---

## Recommendations Summary

### Immediate Actions (This Week)

#### 1. Delete Test Files (38 files)
```bash
# Purge sandbox directory
rm -rf /home/user/tuxedo/sandbox/

# Purge Stellar legacy tests
rm /home/user/tuxedo/backend/test_blend_v2.py
rm /home/user/tuxedo/backend/test_blend_query_fix.py
rm /home/user/tuxedo/backend/test_v2_debug.py
rm /home/user/tuxedo/backend/test_v2_direct.py
rm /home/user/tuxedo/backend/test_current_pools.py
rm /home/user/tuxedo/backend/test_confirmed_v2_pools.py
rm /home/user/tuxedo/backend/test_blnd_emissions.py
rm /home/user/tuxedo/backend/test_storage_keys.py
rm /home/user/tuxedo/backend/test_backstop.py
rm /home/user/tuxedo/backend/test_contract_info.py
rm /home/user/tuxedo/backend/test_contract_methods.py
rm /home/user/tuxedo/backend/test_ledger_entries_simple.py
rm /home/user/tuxedo/backend/test_soroswap_integration.py
rm /home/user/tuxedo/backend/test_with_agent_account.py
```

#### 2. Delete Documentation Files (29+ files)
```bash
# Purge Stellar-specific docs
rm docs/STELLAR_TOOLS_LANGCHAIN_FIX.md
rm docs/STELLAR_WALLETS_KIT_INTEGRATION.md
rm docs/STELLAR_WALLETS_KIT_PROGRESS.md
rm docs/BLEND_YIELD_FARMING_IMPLEMENTATION_PLAN.md
rm docs/blend_query_toolkit.md
rm docs/DEFINDEX_API_NETWORK_PARAMETER_FIX.md
rm docs/DEFINDEX_COMPREHENSIVE_GUIDE.md

# Purge vault/deployment docs
rm docs/VAULT_IMPLEMENTATION_COMPLETE.md
rm docs/VAULT_DEPLOYMENT_COMPLETE.md
rm docs/VAULT_DEPLOYMENT_GUIDE.md
rm docs/VAULT_IMPLEMENTATION_PLAN.md
rm docs/VAULT_COLLATERAL_ARCHITECTURE.md
rm docs/DEPLOYED_TESTNET_INFRASTRUCTURE.md
rm docs/DEPLOYMENT_FINAL_SUMMARY.md
rm docs/DEPLOYMENT_SUCCESS_REPORT.md
rm docs/STRATEGY_DEPLOYMENT_SUMMARY.md
rm docs/MAINNET_INTEGRATION_PLAN.md
rm docs/creative_vault_strategy_design.md
rm docs/playful_path_to_vaults.md

# Purge backend docs
rm backend/BLEND_V2_IMPLEMENTATION_SUCCESS.md
rm backend/BLND_EMISSIONS_IMPLEMENTATION_STATUS.md
rm backend/BLEND_V1_VS_V2_FINDING.md
rm backend/BLEND_QUERY_COMPLETE_SOLUTION.md
rm backend/BLEND_QUERY_FIX.md
rm backend/SOROSWAP_INTEGRATION_COMPLETE.md
rm backend/LAYER2_TESTING_SESSION_REPORT.md
rm backend/READY_TO_TEST.md  # If exists

# Purge root-level hackathon docs
rm VAULT_MVP_SUMMARY.md
rm SOROSWAP_IMPLEMENTATION_SUMMARY.md
rm BLEND_QUERY_TESTING_REPORT.md
rm LAYER_2_TESTING_PROGRESS.md
rm LAYER_2_TESTING_PROGRESS_REPORT.md
rm tux0_vault_implementation_progress.md
rm CLAUDE_SDK_SETUP_COMPLETE.md  # Superseded by docs/CLAUDE_SDK_INTEGRATION.md
rm SOROSWAP_TOOL_IMPLEMENTATION_GUIDE.md
rm DEFINDEX_RESTORATION_GUIDE.md
rm DEFINDEX_RESTORATION_COMPLETE.md
```

#### 3. Rewrite CLAUDE.md ⚠️ CRITICAL

Current CLAUDE.md is **severely outdated** and contradicts the actual project vision.

**Current Issues**:
- Claims Tuxedo is "exclusively on mainnet" with deployed vaults
- Describes 19 Stellar/Blend tools as current implementation
- No mention of Choir or Ghostwriter
- References TUX0 vault extensively (never deployed)
- Contradicts MULTICHAIN_EVM_MIGRATION_PLAN.md

**Required Sections**:
```markdown
# CLAUDE.md

## Project Overview
**Choir** (formerly Tuxedo) is AI research infrastructure for the learning economy.

**Current State**: Ghostwriter foundation complete, multichain migration in planning

**Core Product**: Ghostwriter - AI agent for research, writing, and citation economics

## Architecture
- Multi-model AI orchestration (8-stage research pipeline)
- Passkey authentication (WebAuthn, production-proven)
- Multi-user isolation via AccountManager
- Optional multichain DeFi (planned, not yet implemented)

## Current Features
1. **Ghostwriter**: Research and writing pipeline with verification
2. **Passkey Auth**: WebAuthn biometric authentication
3. **Multi-user**: Isolated accounts and sessions
4. **Chat Interface**: Conversational AI with tool execution

## Future Features (Not Yet Implemented)
- Multichain vault system (Base → EVM chains)
- Citation economics and rewards
- Automated yield farming (EVM-based)

## Development Commands
[Keep existing commands section]

## Important Notes
- **No deployed smart contracts** - vaults are planned but not live
- **Stellar code exists** but is legacy from hackathon phase
- **Multichain is the direction** - see docs/MULTICHAIN_EVM_MIGRATION_PLAN.md
- **Ghostwriter is the focus** - research and writing infrastructure
```

#### 4. Create docs/CURRENT_IMPLEMENTATION_STATUS.md

Create a new doc that clearly states what's implemented vs planned:

```markdown
# Current Implementation Status

## ✅ Implemented and Working
- Ghostwriter pipeline (research, verification, writing)
- Passkey authentication system
- Multi-user account isolation
- Chat interface with AI agent
- Tool execution framework
- WebSearch integration (Tavily)

## 🚧 In Progress
- Multichain migration planning
- Citation economics design
- Knowledge base architecture

## 📋 Planned (Not Started)
- Base/EVM smart contracts
- Vault system deployment
- Automated yield farming
- Cross-chain operations
- Citation reward distribution

## ❌ Deprecated
- Stellar-specific vault implementation
- Blend Capital integration
- DeFindex strategies
- Soroswap integration
```

### Medium-Term Actions (Next 2 Weeks)

#### 1. Update Agent/Chat Tests
- Make tests chain-agnostic
- Remove Stellar-specific assertions
- Add configuration for chain selection
- Update test data to use mock chains

#### 2. Review and Merge Security Docs
- Consolidate 4 security docs into single `docs/SECURITY_ARCHITECTURE.md`
- Remove duplicates and outdated sections

#### 3. Archive Stellar Implementation
Create `docs/STELLAR_LEGACY.md` documenting the Stellar phase:
```markdown
# Stellar Legacy Implementation

This document archives the Stellar-based implementation from the hackathon phase.

## What Was Built
- 6 Stellar tools (accounts, market data, trading, trustlines, utilities, soroban)
- 6 Blend Capital tools (pool discovery, APY queries, supply/withdraw)
- 7 Vault tools (undeployed contracts)

## Why Deprecated
- Multichain pivot to Base (EVM)
- Vault contracts never deployed
- Stellar ecosystem too small for long-term vision

## Code Location
- backend/stellar_tools.py
- backend/blend_pool_tools.py
- backend/vault_tools.py (references undeployed contracts)

## Migration Path
See docs/MULTICHAIN_EVM_MIGRATION_PLAN.md for EVM migration plan.
```

### Long-Term Actions (Next Month)

#### 1. Implement Basic Test Suite
Create minimal test coverage for core features:
- `tests/test_ghostwriter.py` - Pipeline tests
- `tests/test_passkey_auth.py` - Auth flow tests
- `tests/test_agent_core.py` - Agent orchestration tests
- `tests/test_account_isolation.py` - Multi-user isolation tests

#### 2. Documentation Reorganization
```
docs/
├── README.md (overview and navigation)
├── architecture/
│   ├── CHOIR_WHITEPAPER.md
│   ├── MULTICHAIN_EVM_MIGRATION_PLAN.md
│   ├── SECURITY_ARCHITECTURE.md (consolidated)
│   └── PASSKEY_ARCHITECTURE_V2.md
├── ghostwriter/
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PIPELINE_DESIGN.md
│   └── WEBSEARCH_SETUP.md
├── development/
│   ├── ENVIRONMENT_SETUP.md
│   ├── TESTING_STRATEGY.md
│   └── AWS_BEDROCK_CONFIGURATION.md
└── legacy/
    └── STELLAR_LEGACY.md (archive)
```

---

## Risk Assessment

### Risks of Purging Files

| Risk | Mitigation |
|------|------------|
| Losing important context | All files remain in git history |
| Breaking existing workflows | Tests being deleted are not in CI/CD |
| Team member confusion | This document provides clear rationale |
| Need to reference old code | Git history + STELLAR_LEGACY.md archive |

### Risks of NOT Purging Files

| Risk | Impact |
|------|--------|
| Developer confusion | High - CLAUDE.md contradicts actual vision |
| Wasted time | High - developers debug "deployed" vaults that don't exist |
| Onboarding friction | High - new contributors see 51 test files and 45 docs |
| Technical debt accumulation | Medium - outdated code stays in codebase |
| False sense of completeness | High - docs claim features are "complete" when not deployed |

**Recommendation**: Purge is low-risk, high-benefit. Proceed with deletions.

---

## Alternative: Deprecation vs Deletion

If you prefer a more conservative approach:

### Option A: Aggressive Cleanup (Recommended)
- Delete all 38 test files
- Delete all 29 documentation files
- Keep only git history for reference

### Option B: Deprecation Archive
Create `deprecated/` directories:
```bash
mkdir deprecated
mkdir deprecated/tests
mkdir deprecated/docs

# Move instead of delete
mv sandbox/ deprecated/tests/sandbox/
mv backend/test_blend_*.py deprecated/tests/
mv docs/VAULT_*.md deprecated/docs/
# etc.
```

Add `deprecated/README.md`:
```markdown
# Deprecated Code Archive

This directory contains code from the Stellar hackathon phase.
It is not maintained and may not work.
Refer to git history for full context.

**Do not use this code for new development.**
```

**Recommendation**: Option A (delete) is cleaner. Deprecation archive adds clutter.

---

## Implementation Plan

### Phase 1: Immediate Cleanup (This PR)
1. Delete 38 test files (24 sandbox + 14 Stellar legacy)
2. Delete 29 documentation files
3. Rewrite CLAUDE.md
4. Create docs/CURRENT_IMPLEMENTATION_STATUS.md
5. Commit with message: "chore: purge hackathon-era tests and outdated docs"

### Phase 2: Test Updates (Week 2)
1. Update 11 agent/chat tests to be chain-agnostic
2. Review and consolidate security docs
3. Create docs/STELLAR_LEGACY.md archive

### Phase 3: Documentation Reorganization (Week 3-4)
1. Reorganize `/docs` into logical subdirectories
2. Create navigation README for docs
3. Archive remaining outdated content

### Phase 4: Test Suite Rebuild (Month 2)
1. Create systematic test suite for core features
2. Add CI/CD integration
3. Remove remaining legacy tests

---

## Conclusion

**Current State**: Repository has significant technical debt from hackathon phase

**Root Cause**: Vision shifted from Stellar-only DeFi to multichain Choir/Ghostwriter, but old code/docs remain

**Impact**:
- CLAUDE.md actively misleads about deployed features
- 51 test files create confusion (most are one-off experiments)
- 45 docs contain mix of current and outdated information

**Solution**: Aggressive cleanup now prevents compounding confusion

**Recommendation**: Proceed with Phase 1 immediately (delete 67 files, rewrite CLAUDE.md)

**Confidence**: High - all files recoverable from git history, low risk of losing important context

---

## Appendix: File Counts

| Category | Count | Action |
|----------|-------|--------|
| Test files total | 51 | |
| - Ghostwriter tests | 5 | ✅ Keep |
| - Stellar legacy tests | 14 | ❌ Delete |
| - Agent/chat tests | 11 | 🔄 Update |
| - Sandbox tests | 24 | ❌ Delete |
| **Tests to delete** | **38** | |
| | | |
| Documentation total | 45+ | |
| - Current/relevant | 16 | ✅ Keep |
| - Needs major update | 1 | 🔄 Rewrite (CLAUDE.md) |
| - Review/consolidate | 14 | 🔄 Review |
| - Outdated hackathon | 29+ | ❌ Delete |
| **Docs to delete** | **29+** | |
| | | |
| **Total files to purge** | **67+** | |

---

**Document Status**: Ready for review
**Next Action**: Obtain approval and execute Phase 1 cleanup
**Estimated Time**: 1-2 hours for Phase 1 execution
