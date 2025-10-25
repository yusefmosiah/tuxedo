# Blend Protocol Integration Guide

This project is configured to interact with **Blend Protocol** on Stellar Testnet.

## 🎯 What's Configured

### Network Configuration
- **Network**: Stellar Testnet
- **RPC URL**: https://soroban-testnet.stellar.org
- **Horizon URL**: https://horizon-testnet.stellar.org

### Blend Contracts (Testnet)
```typescript
// Core Contracts
Pool Factory: CDSMKKCWEAYQW4DAUSH3XGRMIVIJB44TZ3UA5YCRHT6MP4LWEWR4GYV6
Backstop:     CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X
Emitter:      CCS5ACKIDOIVW2QMWBF7H3ZM4ZIH2Q2NP7I3P3GH7YXXGN7I3WND3D6G

// Tokens
BLND Token:   CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK6A2JN3HEX56T2EDAFO7QF
USDC Token:   CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU
XLM Token:    CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC

// Pools
Comet Pool:   CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF
```

## 📦 Installed Dependencies

- `@blend-capital/blend-sdk` - Official Blend SDK for contract interactions
- `@stellar/stellar-sdk` - Stellar SDK for blockchain operations
- `@creit.tech/stellar-wallets-kit` - Wallet connection

## 🚀 Quick Start

### 1. Start the Development Server
```bash
npm run dev
```

Open http://localhost:5174 to see the app.

### 2. Connect Your Wallet
- Click "Connect Account" in the top right
- Select a wallet (Freighter, xBull, etc.)
- Approve the connection

### 3. Fund Your Account (Testnet)
- After connecting, click "Fund Account with Friendbot"
- Wait for the transaction to complete
- You now have testnet XLM to interact with Blend!

## 💻 Code Examples

### Query Pool Data (Read-Only)

```typescript
import { PoolContract } from "@blend-capital/blend-sdk";
import { SorobanRpc, Account, Keypair } from "@stellar/stellar-sdk";

const rpcUrl = "https://soroban-testnet.stellar.org";
const poolAddress = "CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF";

async function queryPoolPositions() {
  // Create RPC server
  const server = new SorobanRpc.Server(rpcUrl);

  // Create a dummy account for simulation
  const dummyKeypair = Keypair.random();
  const dummyAccount = new Account(dummyKeypair.publicKey(), "0");

  // Initialize pool contract
  const pool = new PoolContract(poolAddress);

  // Build transaction (simulation only, not submitted)
  const tx = await pool.get_positions({
    // Add required parameters here
  });

  // Simulate to get result
  const result = await server.simulateTransaction(tx);

  // Parse result
  console.log(result);
}
```

### Supply Assets to Pool (Write Operation)

```typescript
import { PoolContract } from "@blend-capital/blend-sdk";
import {
  SorobanRpc,
  Account,
  TransactionBuilder,
  BASE_FEE
} from "@stellar/stellar-sdk";

async function supplyToPool(
  userPublicKey: string,
  amount: bigint,
  assetId: string
) {
  const server = new SorobanRpc.Server(rpcUrl);
  const networkPassphrase = "Test SDF Network ; September 2015";

  // Get user account
  const account = await server.getAccount(userPublicKey);

  // Initialize pool
  const pool = new PoolContract(poolAddress);

  // Build supply operation
  const operation = pool.submit({
    from: userPublicKey,
    to: userPublicKey,
    spender: userPublicKey,
    amount: amount,
    // ... other required params
  });

  // Build transaction
  const tx = new TransactionBuilder(account, {
    fee: BASE_FEE,
    networkPassphrase,
  })
    .addOperation(operation)
    .setTimeout(30)
    .build();

  // Prepare transaction
  const prepared = await server.prepareTransaction(tx);

  // Sign with wallet (user approval required)
  // const signed = await walletKit.sign(prepared);

  // Submit to network
  // const result = await server.sendTransaction(signed);

  return prepared;
}
```

### Using React Hooks

```typescript
// In your component
import { useBlendPool } from "../hooks/useBlendPool";
import { BLEND_CONTRACTS } from "../contracts/blend";

function MyComponent() {
  const poolData = useBlendPool(BLEND_CONTRACTS.cometPool);

  if (poolData.loading) return <div>Loading pool data...</div>;
  if (poolData.error) return <div>Error: {poolData.error}</div>;

  return (
    <div>
      <h3>Pool: {poolData.poolId}</h3>
      {/* Display pool data */}
    </div>
  );
}
```

## 📚 Key Concepts

### Read Operations (No Wallet Required)
- Query pool positions
- Get reserve data
- Check pool configuration
- View APY rates
- **Method**: Use `server.simulateTransaction()`

### Write Operations (Wallet Required)
- Supply assets
- Borrow assets
- Repay loans
- Withdraw funds
- **Method**: Build, sign, and submit transactions

## 🔗 Useful Resources

- [Blend Docs](https://docs.blend.capital/)
- [Blend SDK GitHub](https://github.com/blend-capital/blend-sdk)
- [Blend Pool Integration Guide](https://docs.blend.capital/tech-docs/integrations/integrate-pool)
- [Stellar Soroban Docs](https://developers.stellar.org/docs/build/smart-contracts)
- [Stellar SDK Docs](https://stellar.github.io/js-stellar-sdk/)

## 🛠️ Project Structure

```
src/
├── contracts/
│   ├── blend.ts              # Blend contract addresses and helpers
│   └── util.ts               # Network configuration utilities
├── hooks/
│   ├── useBlendPool.ts       # Hook for querying pool data
│   ├── useWallet.ts          # Wallet connection hook
│   └── useWalletBalance.ts   # Check wallet balances
├── components/
│   ├── BlendPoolViewer.tsx   # Display Blend contracts
│   ├── BlendPoolQuery.tsx    # Interactive query examples
│   └── ConnectAccount.tsx    # Wallet connection UI
└── pages/
    └── Home.tsx              # Main page with Blend integration
```

## ⚠️ Important Notes

1. **Testnet Only**: This configuration uses testnet. For mainnet, update:
   - `.env` with mainnet RPC URLs
   - `environments.toml` with mainnet contract addresses

2. **Gas Fees**: All transactions require XLM for fees. Fund your account with Friendbot on testnet.

3. **Contract Methods**: Blend SDK provides typed methods for all pool operations. Check the SDK docs for full API.

4. **Error Handling**: Always wrap contract calls in try-catch blocks and handle RPC errors gracefully.

## 🐛 Troubleshooting

### "Failed to fetch" errors
- Check your RPC URL is correct
- Verify network connection
- Testnet RPC may be rate-limited

### "Account not found"
- Fund your account with Friendbot
- Wait a few seconds for the ledger to update

### "Transaction failed"
- Check you have sufficient balance
- Verify contract parameters are correct
- Look at the error message in the console

## 📝 Next Steps

1. ✅ Environment configured for testnet
2. ✅ Blend SDK installed
3. ✅ Contract addresses added
4. ✅ Example components created
5. 🔲 Implement real pool queries
6. 🔲 Add supply/borrow UI
7. 🔲 Create position management interface
8. 🔲 Add transaction history

Happy building! 🚀
