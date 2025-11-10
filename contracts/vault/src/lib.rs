#![no_std]

use soroban_sdk::{
    contract, contracterror, contractimpl, contracttype, Address, Env, Symbol, symbol_short,
    token,
};

// ============ Constants ============
const ADMIN: Symbol = symbol_short!("ADMIN");
const AGENT: Symbol = symbol_short!("AGENT");
const PLATFORM: Symbol = symbol_short!("PLATFORM");
const TOTAL_SHARES: Symbol = symbol_short!("T_SHARES");
const INITIAL_DEPOSITS: Symbol = symbol_short!("INIT_DEP");
const SHARE_TOKEN: Symbol = symbol_short!("SHR_TKN");

// Initial share value: 1 USDC = 1 TUX0 (with 7 decimals)
const INITIAL_SHARE_VALUE: i128 = 10_000_000; // 1.0000000

// Fee structure: 2% to platform, 98% stays with users
const PLATFORM_FEE_BPS: i128 = 200; // 2% in basis points
const BPS_DENOMINATOR: i128 = 10_000; // 100% = 10,000 basis points

// ============ Errors ============
#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum VaultError {
    AlreadyInitialized = 1,
    NotAuthorized = 2,
    InvalidAmount = 3,
    InsufficientShares = 4,
    InsufficientBalance = 5,
    NoYieldToDistribute = 6,
    InvalidAsset = 7,
    TransferFailed = 8,
    DivisionByZero = 9,
}

// ============ Data Structures ============
#[contracttype]
#[derive(Clone)]
pub struct VaultStats {
    pub total_assets: i128,
    pub total_shares: i128,
    pub share_value: i128,
    pub initial_deposits: i128,
}

#[contracttype]
#[derive(Clone)]
pub struct Strategy {
    pub action: Symbol, // "supply" or "withdraw"
    pub pool: Address,
    pub asset: Address,
    pub amount: i128,
}

// ============ TuxedoVault Smart Contract ============
#[contract]
pub struct TuxedoVault;

#[contractimpl]
impl TuxedoVault {
    /// Initialize the vault with admin, agent, and platform addresses
    pub fn initialize(
        env: Env,
        admin: Address,
        agent: Address,
        platform: Address,
        usdc_asset: Address,
    ) -> Result<(), VaultError> {
        // Check if already initialized
        if env.storage().instance().has(&ADMIN) {
            return Err(VaultError::AlreadyInitialized);
        }

        // Set initial state
        env.storage().instance().set(&ADMIN, &admin);
        env.storage().instance().set(&AGENT, &agent);
        env.storage().instance().set(&PLATFORM, &platform);
        env.storage().instance().set(&SHARE_TOKEN, &usdc_asset);
        env.storage().instance().set(&TOTAL_SHARES, &0i128);
        env.storage().instance().set(&INITIAL_DEPOSITS, &0i128);

        // Emit initialization event
        env.events().publish(
            (symbol_short!("vault"), symbol_short!("init")),
            (admin, agent, platform),
        );

        Ok(())
    }

    /// User deposits USDC and receives vault shares (TUX0)
    pub fn deposit(
        env: Env,
        user: Address,
        amount: i128,
    ) -> Result<i128, VaultError> {
        user.require_auth();

        // Validate amount
        if amount <= 0 {
            return Err(VaultError::InvalidAmount);
        }

        // Get USDC asset
        let usdc_asset: Address = env.storage().instance().get(&SHARE_TOKEN).unwrap();

        // Calculate current share value
        let share_value = Self::calculate_share_value(&env);

        // Calculate shares to mint
        let shares_to_mint = if share_value == 0 {
            // First deposit: 1:1 ratio
            amount
        } else {
            // shares = amount / share_value
            // Using fixed-point arithmetic: amount * 10^7 / share_value
            (amount * INITIAL_SHARE_VALUE) / share_value
        };

        if shares_to_mint <= 0 {
            return Err(VaultError::InvalidAmount);
        }

        // Transfer USDC from user to vault
        let token_client = token::TokenClient::new(&env, &usdc_asset);
        token_client.transfer(&user, &env.current_contract_address(), &amount);

        // Update total shares
        let total_shares: i128 = env.storage().instance().get(&TOTAL_SHARES).unwrap_or(0);
        env.storage().instance().set(&TOTAL_SHARES, &(total_shares + shares_to_mint));

        // Update initial deposits tracking
        let initial_deposits: i128 = env.storage().instance().get(&INITIAL_DEPOSITS).unwrap_or(0);
        env.storage().instance().set(&INITIAL_DEPOSITS, &(initial_deposits + amount));

        // Update user's share balance
        let user_shares_key = (symbol_short!("shares"), user.clone());
        let current_user_shares: i128 = env.storage().persistent().get(&user_shares_key).unwrap_or(0);
        env.storage().persistent().set(&user_shares_key, &(current_user_shares + shares_to_mint));

        // Emit deposit event
        env.events().publish(
            (symbol_short!("vault"), symbol_short!("deposit")),
            (user, amount, shares_to_mint),
        );

        Ok(shares_to_mint)
    }

    /// User burns shares and receives proportional USDC
    pub fn withdraw(
        env: Env,
        user: Address,
        shares: i128,
    ) -> Result<i128, VaultError> {
        user.require_auth();

        // Validate shares
        if shares <= 0 {
            return Err(VaultError::InvalidAmount);
        }

        // Check user has enough shares
        let user_shares_key = (symbol_short!("shares"), user.clone());
        let user_shares: i128 = env.storage().persistent().get(&user_shares_key).unwrap_or(0);

        if user_shares < shares {
            return Err(VaultError::InsufficientShares);
        }

        // Calculate current share value
        let share_value = Self::calculate_share_value(&env);

        // Calculate USDC to return
        // assets = shares * share_value / 10^7
        let assets_to_return = (shares * share_value) / INITIAL_SHARE_VALUE;

        if assets_to_return <= 0 {
            return Err(VaultError::InvalidAmount);
        }

        // Get total vault assets
        let total_assets = Self::get_total_vault_assets(&env);

        if total_assets < assets_to_return {
            return Err(VaultError::InsufficientBalance);
        }

        // Update user's share balance
        let new_user_shares = user_shares - shares;
        if new_user_shares == 0 {
            env.storage().persistent().remove(&user_shares_key);
        } else {
            env.storage().persistent().set(&user_shares_key, &new_user_shares);
        }

        // Update total shares
        let total_shares: i128 = env.storage().instance().get(&TOTAL_SHARES).unwrap_or(0);
        env.storage().instance().set(&TOTAL_SHARES, &(total_shares - shares));

        // Update initial deposits proportionally
        let initial_deposits: i128 = env.storage().instance().get(&INITIAL_DEPOSITS).unwrap_or(0);
        let deposit_reduction = if total_shares > 0 {
            (initial_deposits * shares) / total_shares
        } else {
            initial_deposits
        };
        env.storage().instance().set(&INITIAL_DEPOSITS, &(initial_deposits - deposit_reduction));

        // Transfer USDC back to user
        let usdc_asset: Address = env.storage().instance().get(&SHARE_TOKEN).unwrap();
        let token_client = token::TokenClient::new(&env, &usdc_asset);
        token_client.transfer(&env.current_contract_address(), &user, &assets_to_return);

        // Emit withdraw event
        env.events().publish(
            (symbol_short!("vault"), symbol_short!("withdraw")),
            (user, shares, assets_to_return),
        );

        Ok(assets_to_return)
    }

    /// Agent executes a yield strategy (Blend supply/withdraw)
    /// Only the authorized agent can call this
    pub fn agent_execute(
        env: Env,
        strategy: Strategy,
    ) -> Result<(), VaultError> {
        // Verify agent authorization
        let agent: Address = env.storage().instance().get(&AGENT).unwrap();
        agent.require_auth();

        // Validate amount
        if strategy.amount <= 0 {
            return Err(VaultError::InvalidAmount);
        }

        // Clone action for later use in event
        let action = strategy.action.clone();

        // Execute strategy based on action
        match strategy.action {
            ref act if *act == symbol_short!("supply") => {
                // Supply assets to Blend pool
                let token_client = token::TokenClient::new(&env, &strategy.asset);
                token_client.transfer(
                    &env.current_contract_address(),
                    &strategy.pool,
                    &strategy.amount,
                );
            }
            ref act if *act == symbol_short!("withdraw") => {
                // Withdraw assets from Blend pool
                // Note: This is simplified. Real implementation would call Blend contract
                let token_client = token::TokenClient::new(&env, &strategy.asset);
                token_client.transfer(
                    &strategy.pool,
                    &env.current_contract_address(),
                    &strategy.amount,
                );
            }
            _ => {
                return Err(VaultError::NotAuthorized);
            }
        }

        // Emit strategy execution event
        env.events().publish(
            (symbol_short!("vault"), symbol_short!("strategy")),
            (agent, action, strategy.amount),
        );

        Ok(())
    }

    /// Distribute yield: 98% stays in vault (for users), 2% to platform
    /// Anyone can call this function
    pub fn distribute_yield(env: Env) -> Result<(), VaultError> {
        let total_assets = Self::get_total_vault_assets(&env);
        let initial_deposits: i128 = env.storage().instance().get(&INITIAL_DEPOSITS).unwrap_or(0);

        // Calculate yield earned
        let yield_earned = total_assets - initial_deposits;

        if yield_earned <= 0 {
            return Err(VaultError::NoYieldToDistribute);
        }

        // Calculate platform fee: 2%
        let platform_fee = (yield_earned * PLATFORM_FEE_BPS) / BPS_DENOMINATOR;

        if platform_fee <= 0 {
            return Err(VaultError::NoYieldToDistribute);
        }

        // Transfer fee to platform
        let platform: Address = env.storage().instance().get(&PLATFORM).unwrap();
        let usdc_asset: Address = env.storage().instance().get(&SHARE_TOKEN).unwrap();
        let token_client = token::TokenClient::new(&env, &usdc_asset);

        token_client.transfer(&env.current_contract_address(), &platform, &platform_fee);

        // Update initial deposits to reflect the fee taken out
        // This ensures share value reflects the fee distribution
        let new_initial_deposits = initial_deposits + (yield_earned - platform_fee);
        env.storage().instance().set(&INITIAL_DEPOSITS, &new_initial_deposits);

        // Emit yield distribution event
        env.events().publish(
            (symbol_short!("vault"), symbol_short!("yield")),
            (yield_earned, platform_fee),
        );

        Ok(())
    }

    /// Get current share value in USDC (with 7 decimals)
    pub fn get_share_value(env: Env) -> i128 {
        Self::calculate_share_value(&env)
    }

    /// Get total vault assets (USDC balance)
    pub fn get_total_assets(env: Env) -> i128 {
        Self::get_total_vault_assets(&env)
    }

    /// Get total shares issued
    pub fn get_total_shares(env: Env) -> i128 {
        env.storage().instance().get(&TOTAL_SHARES).unwrap_or(0)
    }

    /// Get user's share balance
    pub fn get_user_shares(env: Env, user: Address) -> i128 {
        let user_shares_key = (symbol_short!("shares"), user);
        env.storage().persistent().get(&user_shares_key).unwrap_or(0)
    }

    /// Get vault statistics
    pub fn get_vault_stats(env: Env) -> VaultStats {
        let total_assets = Self::get_total_vault_assets(&env);
        let total_shares: i128 = env.storage().instance().get(&TOTAL_SHARES).unwrap_or(0);
        let share_value = Self::calculate_share_value(&env);
        let initial_deposits: i128 = env.storage().instance().get(&INITIAL_DEPOSITS).unwrap_or(0);

        VaultStats {
            total_assets,
            total_shares,
            share_value,
            initial_deposits,
        }
    }

    /// Get agent address
    pub fn get_agent(env: Env) -> Address {
        env.storage().instance().get(&AGENT).unwrap()
    }

    /// Get platform address
    pub fn get_platform(env: Env) -> Address {
        env.storage().instance().get(&PLATFORM).unwrap()
    }

    /// Get admin address
    pub fn get_admin(env: Env) -> Address {
        env.storage().instance().get(&ADMIN).unwrap()
    }

    // ============ Internal Helper Functions ============

    /// Calculate current share value: total_assets / total_shares
    fn calculate_share_value(env: &Env) -> i128 {
        let total_assets = Self::get_total_vault_assets(env);
        let total_shares: i128 = env.storage().instance().get(&TOTAL_SHARES).unwrap_or(0);

        if total_shares == 0 {
            return INITIAL_SHARE_VALUE; // 1.0 USDC per share
        }

        // share_value = (total_assets * 10^7) / total_shares
        (total_assets * INITIAL_SHARE_VALUE) / total_shares
    }

    /// Get total USDC balance held by the vault
    fn get_total_vault_assets(env: &Env) -> i128 {
        let usdc_asset: Address = env.storage().instance().get(&SHARE_TOKEN).unwrap();
        let token_client = token::TokenClient::new(env, &usdc_asset);
        token_client.balance(&env.current_contract_address())
    }
}

// ============ Tests ============
#[cfg(test)]
mod test {
    use super::*;
    use soroban_sdk::{testutils::Address as _, Address, Env};

    #[test]
    fn test_initialize() {
        let env = Env::default();
        let contract_id = env.register_contract(None, TuxedoVault);
        let client = TuxedoVaultClient::new(&env, &contract_id);

        let admin = Address::generate(&env);
        let agent = Address::generate(&env);
        let platform = Address::generate(&env);
        let usdc = Address::generate(&env);

        client.initialize(&admin, &agent, &platform, &usdc);

        assert_eq!(client.get_admin(), admin);
        assert_eq!(client.get_agent(), agent);
        assert_eq!(client.get_platform(), platform);
    }

    #[test]
    #[should_panic(expected = "AlreadyInitialized")]
    fn test_double_initialize() {
        let env = Env::default();
        let contract_id = env.register_contract(None, TuxedoVault);
        let client = TuxedoVaultClient::new(&env, &contract_id);

        let admin = Address::generate(&env);
        let agent = Address::generate(&env);
        let platform = Address::generate(&env);
        let usdc = Address::generate(&env);

        client.initialize(&admin, &agent, &platform, &usdc);
        client.initialize(&admin, &agent, &platform, &usdc); // Should panic
    }

    #[test]
    fn test_share_value_calculation() {
        let env = Env::default();
        let contract_id = env.register_contract(None, TuxedoVault);
        let client = TuxedoVaultClient::new(&env, &contract_id);

        let admin = Address::generate(&env);
        let agent = Address::generate(&env);
        let platform = Address::generate(&env);
        let usdc = Address::generate(&env);

        client.initialize(&admin, &agent, &platform, &usdc);

        // Initial share value should be 1.0 (10^7)
        let share_value = client.get_share_value();
        assert_eq!(share_value, INITIAL_SHARE_VALUE);
    }
}
