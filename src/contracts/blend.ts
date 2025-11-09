import { Contract, rpc } from "@stellar/stellar-sdk";
// import {
//   PoolContract,
//   BackstopContract,
//   PoolFactoryContract,
// } from "@blend-capital/blend-sdk";
import { rpcUrl, stellarNetwork } from "./util";

/**
 * Blend Protocol Contract Addresses (Mainnet)
 * Source: https://github.com/blend-capital/blend-utils/blob/main/mainnet.contracts.json
 */
export const BLEND_MAINNET_CONTRACTS = {
  // Core Blend V2 Infrastructure
  backstop: "CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7",
  poolFactory: "CDSYOAVXFY7SM5S64IZPPPYB4GVGGLMQVFREPSQQEZVIWXX5R23G4QSU",
  emitter: "CCOQM6S7ICIUWA225O5PSJWUBEMXGFSSW2PQFO6FP4DQEKMS5DASRGRR",

  // Tokens
  blndToken: "CD25MNVTZDL4Y3XBCPCJXGXATV5WUHHOWMYFF4YBEGU5FCPGMYTVG5JY",
  usdcToken: "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75",
  xlmToken: "CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA",

  // Pools
  cometPool: "CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM",
  fixedPool: "CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD",
  yieldBloxPool: "CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS",
} as const;

/**
 * Blend Protocol Contract Addresses (Testnet)
 * Source: https://github.com/blend-capital/blend-utils/blob/main/testnet.contracts.json
 */
export const BLEND_TESTNET_CONTRACTS = {
  // Core Blend V2 Contracts
  poolFactory: "CDSMKKCWEAYQW4DAUSH3XGRMIVIJB44TZ3UA5YCRHT6MP4LWEWR4GYV6",
  backstop: "CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X",
  emitter: "CCS5ACKIDOIVW2QMWBF7H3ZM4ZIH2Q2NP7I3P3GH7YXXGN7I3WND3D6G",

  // Tokens
  blndToken: "CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK6A2JN3HEX56T2EDAFO7QF",
  usdcToken: "CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU",
  xlmToken: "CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC",

  // Pools
  cometPool: "CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF",
} as const;

/**
 * Active contract addresses based on network configuration
 * Defaults to mainnet for production use
 */
export const BLEND_CONTRACTS =
  stellarNetwork === "TESTNET"
    ? BLEND_TESTNET_CONTRACTS
    : BLEND_MAINNET_CONTRACTS;

/**
 * Initialize a Soroban RPC Server instance
 */
export function getServer() {
  return new rpc.Server(rpcUrl, {
    allowHttp: rpcUrl.startsWith("http://"),
  });
}

/**
 * Create a Contract instance for any Blend contract
 */
export function getBlendContract(contractId: string) {
  return new Contract(contractId);
}

/**
 * Helper to get specific Blend contracts using Blend SDK
 */
export const BlendContracts = {
  // Use standard Contract for all (can work with Blend SDK methods)
  poolFactory: () => getBlendContract(BLEND_CONTRACTS.poolFactory),
  backstop: () => getBlendContract(BLEND_CONTRACTS.backstop),
  cometPool: () => getBlendContract(BLEND_CONTRACTS.cometPool),
  blndToken: () => getBlendContract(BLEND_CONTRACTS.blndToken),
  usdcToken: () => getBlendContract(BLEND_CONTRACTS.usdcToken),
  xlmToken: () => getBlendContract(BLEND_CONTRACTS.xlmToken),
} as const;

/**
 * Example: Query pool data from Blend
 *
 * Usage in a React component:
 *
 * ```tsx
 * import { BLEND_CONTRACTS, getServer, getBlendContract } from "../contracts/blend";
 *
 * const contract = getBlendContract(BLEND_CONTRACTS.cometPool);
 * const server = getServer();
 *
 * // Call a read-only method (no wallet signature needed)
 * const result = await server.simulateTransaction(
 *   new TransactionBuilder(account, { fee: "100", networkPassphrase })
 *     .addOperation(contract.call("get_positions", ...args))
 *     .setTimeout(30)
 *     .build()
 * );
 * ```
 *
 * For write operations (supply, borrow, etc.), you'll need to:
 * 1. Connect a wallet using the WalletProvider
 * 2. Build and sign transactions
 * 3. Submit to the network
 */
