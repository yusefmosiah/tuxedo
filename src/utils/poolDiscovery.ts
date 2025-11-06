/**
 * Comprehensive Pool Discovery Utility
 *
 * This utility exhaustively searches for all Blend pools on testnet using multiple strategies:
 * 1. Backstop reward zone (official approach)
 * 2. Pool Factory events (all deployed pools)
 * 3. Known hardcoded pools (fallback)
 */

import { Backstop, PoolV2 } from "@blend-capital/blend-sdk";
import { BLEND_CONTRACTS } from "../contracts/blend";
import { network } from "../contracts/util";

// Create Blend SDK compatible network object
const blendNetwork = {
  rpc: network.rpcUrl,
  passphrase: network.passphrase,
  networkPassphrase: network.passphrase,
};

interface PoolDiscoveryResult {
  backstopPools: string[];
  factoryPools: string[];
  knownPools: string[];
  allPoolsUnique: string[];
}

interface TokenInfo {
  address: string;
  symbol: string;
  decimals: number;
}

interface PoolTokenReport {
  poolAddress: string;
  poolName: string;
  tokens: TokenInfo[];
  tokenCount: number;
}

/**
 * Strategy 1: Get pools from Backstop's reward zone
 * This is the "official" way but may only include active earning pools
 */
export async function discoverPoolsViaBackstop(): Promise<string[]> {
  try {
    console.log("🔍 [Strategy 1] Loading pools from Backstop reward zone...");
    const backstop = await Backstop.load(
      blendNetwork,
      BLEND_CONTRACTS.backstop,
    );

    const pools = backstop.config.rewardZone;
    console.log(
      `  ✅ Found ${pools.length} pool(s) in Backstop reward zone:`,
      pools,
    );

    return pools;
  } catch (err) {
    console.error("  ❌ Failed to get pools from Backstop:", err);
    return [];
  }
}

/**
 * Strategy 2: Get pools from Pool Factory events
 * This finds ALL pools ever deployed
 *
 * NOTE: Currently disabled due to event query complexity and ledger history limitations
 * Can be re-enabled once Stellar RPC event querying is fully tested
 */
export async function discoverPoolsViaFactory(): Promise<string[]> {
  console.log(
    "🔍 [Strategy 2] Pool Factory event discovery disabled (use Backstop + known pools)",
  );
  // TODO: Re-implement once event handling is stable
  return [];
}

/**
 * Strategy 3: Use known hardcoded pools
 * Fallback for when network queries fail
 */
export function getKnownPools(): string[] {
  return [
    BLEND_CONTRACTS.cometPool, // Comet - definitely exists
    // Add more known pool addresses here as discovered
  ];
}

/**
 * Main discovery function - uses all strategies
 */
export async function discoverAllPools(): Promise<PoolDiscoveryResult> {
  console.log("\n🌊 === COMPREHENSIVE POOL DISCOVERY ===\n");

  const [backstopPools, factoryPools] = await Promise.all([
    discoverPoolsViaBackstop(),
    discoverPoolsViaFactory(),
  ]);

  const knownPools = getKnownPools();

  // Merge all pools (remove duplicates)
  const allPoolsSet = new Set<string>([
    ...backstopPools,
    ...factoryPools,
    ...knownPools,
  ]);

  const result: PoolDiscoveryResult = {
    backstopPools,
    factoryPools,
    knownPools,
    allPoolsUnique: Array.from(allPoolsSet),
  };

  console.log("\n📊 === DISCOVERY SUMMARY ===");
  console.log(`  Backstop pools: ${backstopPools.length}`);
  console.log(`  Factory pools: ${factoryPools.length}`);
  console.log(`  Known pools: ${knownPools.length}`);
  console.log(`  Total unique: ${result.allPoolsUnique.length}`);
  console.log("\nAll unique pool addresses:");
  result.allPoolsUnique.forEach((pool, i) => {
    console.log(`  ${i + 1}. ${pool}`);
  });

  return result;
}

/**
 * Extract all tokens from a pool
 */
export async function getPoolTokens(poolAddress: string): Promise<TokenInfo[]> {
  try {
    const pool = await PoolV2.load(blendNetwork, poolAddress);

    const tokens: TokenInfo[] = [];

    for (const [assetId] of pool.reserves) {
      // Try to infer token info (we'll need to fetch metadata)
      tokens.push({
        address: assetId,
        symbol: assetId.slice(0, 8), // Short form, will be replaced with metadata
        decimals: 7, // Most Stellar tokens use 7 decimals
      });
    }

    return tokens;
  } catch (err) {
    console.error(`Failed to load tokens for pool ${poolAddress}:`, err);
    return [];
  }
}

/**
 * Generate comprehensive report of all pools and their tokens
 */
export async function generatePoolTokenReport(): Promise<PoolTokenReport[]> {
  console.log("\n🎫 === TOKEN DISCOVERY ===\n");

  const discovery = await discoverAllPools();
  const reports: PoolTokenReport[] = [];

  for (const poolAddress of discovery.allPoolsUnique) {
    try {
      console.log(`\n📦 Loading tokens for pool: ${poolAddress}`);

      const pool = await PoolV2.load(blendNetwork, poolAddress);
      const tokens = Array.from(pool.reserves.keys()).map((assetId) => ({
        address: assetId,
        symbol: assetId.slice(0, 8),
        decimals: 7,
      }));

      console.log(`  ✅ Found ${tokens.length} tokens:`);
      tokens.forEach((token) => {
        console.log(`    💰 ${token.address}`);
      });

      reports.push({
        poolAddress,
        poolName: pool.metadata.name || `Pool ${poolAddress.slice(0, 8)}`,
        tokens,
        tokenCount: tokens.length,
      });
    } catch (err) {
      console.error(`  ❌ Failed to load pool ${poolAddress}:`, err);
    }
  }

  console.log("\n📊 === TOKEN SUMMARY ===");

  // Collect all unique tokens
  const allTokensSet = new Set<string>();
  reports.forEach((report) => {
    report.tokens.forEach((token) => {
      allTokensSet.add(token.address);
    });
  });

  console.log(`Total unique tokens across all pools: ${allTokensSet.size}`);
  console.log("\nAll token addresses:");
  Array.from(allTokensSet).forEach((token, i) => {
    console.log(`  ${i + 1}. ${token}`);
  });

  return reports;
}

/**
 * Log comprehensive statistics
 */
export async function logPoolStats(): Promise<void> {
  const discovery = await discoverAllPools();
  const reports = await generatePoolTokenReport();

  console.log(
    "\n\n═══════════════════════════════════════════════════════════",
  );
  console.log("📊 COMPREHENSIVE BLEND POOLS ANALYSIS");
  console.log("═══════════════════════════════════════════════════════════\n");

  console.log("🏊 POOLS:");
  discovery.allPoolsUnique.forEach((pool, i) => {
    const report = reports.find((r) => r.poolAddress === pool);
    console.log(`  ${i + 1}. ${pool}`);
    console.log(`     Name: ${report?.poolName || "Unknown"}`);
    console.log(`     Tokens: ${report?.tokenCount || 0}`);
    if (report?.tokens) {
      report.tokens.forEach((token) => {
        console.log(`       - ${token.address}`);
      });
    }
  });

  console.log("\n💰 TOKENS (All unique tokens across all pools):");
  const allTokens = new Set<string>();
  reports.forEach((report) => {
    report.tokens.forEach((token) => {
      allTokens.add(token.address);
    });
  });

  const tokenArray = Array.from(allTokens);
  tokenArray.forEach((token, i) => {
    console.log(`  ${i + 1}. ${token}`);
  });

  console.log(
    `\n✅ Total: ${discovery.allPoolsUnique.length} pools, ${tokenArray.length} unique tokens`,
  );
  console.log("═══════════════════════════════════════════════════════════\n");
}
