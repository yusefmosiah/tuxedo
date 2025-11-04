#![no_std]
use soroban_sdk::{contract, contractimpl, token, Address, Env, Map};

/// TUX Token - Tuxedo Universal eXchange Token
/// Governance, access control, and yield distribution token for the Tuxedo ecosystem
#[contract]
pub struct TuxToken;

// Token metadata
const TOKEN_DECIMALS: u32 = 7;
const TOKEN_SYMBOL: &str = "TUX";
const TOKEN_NAME: &str = "Tuxedo Universal eXchange Token";

// Tier thresholds in TUX tokens
const BRONZE_TIER: i128 = 100_i128 * 10i128.pow(TOKEN_DECIMALS); // 100 TUX
const SILVER_TIER: i128 = 1000_i128 * 10i128.pow(TOKEN_DECIMALS); // 1000 TUX
const GOLD_TIER: i128 = 10000_i128 * 10i128.pow(TOKEN_DECIMALS); // 10000 TUX

#[derive(Copy, Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub enum ParticipationTier {
    Free = 0,
    Bronze = 1,
    Silver = 2,
    Gold = 3,
}

#[contractimpl]
impl TuxToken {
    /// Initialize the TUX token contract
    ///
    /// # Arguments
    /// * `admin` - The admin address that can mint tokens
    /// * `initial_supply` - Initial supply to mint to admin
    pub fn initialize(env: Env, admin: Address, initial_supply: i128) {
        // Store admin
        env.storage().instance().set(&symbol!("admin"), &admin);

        // Store token metadata
        env.storage().instance().set(&symbol!("name"), &TOKEN_NAME);
        env.storage().instance().set(&symbol!("symbol"), &TOKEN_SYMBOL);
        env.storage().instance().set(&symbol!("decimals"), &TOKEN_DECIMALS);

        // Store initial tier config
        env.storage().instance().set(&symbol!("bronze_tier"), &BRONZE_TIER);
        env.storage().instance().set(&symbol!("silver_tier"), &SILVER_TIER);
        env.storage().instance().set(&symbol!("gold_tier"), &GOLD_TIER);

        // Initialize user tiers map
        let user_tiers: Map<Address, ParticipationTier> = Map::new(&env);
        env.storage().instance().set(&symbol!("user_tiers"), &user_tiers);

        // Initialize staking map (address -> staked amount)
        let staking: Map<Address, i128> = Map::new(&env);
        env.storage().instance().set(&symbol!("staking"), &staking);

        // Mint initial supply to admin
        if initial_supply > 0 {
            let token_client = token::Client::new(&env, &env.current_contract_address());
            token_client.mint(&admin, &initial_supply);
        }
    }

    /// Get the token name
    pub fn name(env: Env) -> String {
        env.storage().instance()
            .get(&symbol!("name"))
            .unwrap_or_default()
    }

    /// Get the token symbol
    pub fn symbol(env: Env) -> String {
        env.storage().instance()
            .get(&symbol!("symbol"))
            .unwrap_or_default()
    }

    /// Get the token decimals
    pub fn decimals(env: Env) -> u32 {
        env.storage().instance()
            .get(&symbol!("decimals"))
            .unwrap_or(TOKEN_DECIMALS)
    }

    /// Get the current admin
    pub fn get_admin(env: Env) -> Address {
        env.storage().instance()
            .get(&symbol!("admin"))
            .unwrap()
    }

    /// Get user's current participation tier based on TUX balance
    pub fn get_user_tier(env: Env, user: Address) -> ParticipationTier {
        let token_client = token::Client::new(&env, &env.current_contract_address());
        let balance = token_client.balance(&user);

        // Check balance against tier thresholds
        if balance >= GOLD_TIER {
            ParticipationTier::Gold
        } else if balance >= SILVER_TIER {
            ParticipationTier::Silver
        } else if balance >= BRONZE_TIER {
            ParticipationTier::Bronze
        } else {
            ParticipationTier::Free
        }
    }

    /// Check if user can access a specific tier feature
    pub fn can_access_tier(env: Env, user: Address, required_tier: ParticipationTier) -> bool {
        let user_tier = Self::get_user_tier(env, user);
        user_tier >= required_tier
    }

    /// Stake TUX tokens for additional benefits
    ///
    /// # Arguments
    /// * `amount` - Amount of TUX to stake
    pub fn stake(env: Env, amount: i128) {
        let user = env.current_contract_address();
        let token_client = token::Client::new(&env, &env.current_contract_address());

        // Transfer tokens to contract (staking)
        token_client.transfer(&user, &env.current_contract_address(), &amount);

        // Update staking amount
        let mut staking: Map<Address, i128> = env.storage().instance()
            .get(&symbol!("staking"))
            .unwrap_or(Map::new(&env));

        let current_stake = staking.get(user).unwrap_or(0);
        staking.set(user, current_stake + amount);
        env.storage().instance().set(&symbol!("staking"), &staking);
    }

    /// Unstake TUX tokens
    ///
    /// # Arguments
    /// * `amount` - Amount of TUX to unstake
    pub fn unstake(env: Env, amount: i128) {
        let user = env.current_contract_address();

        // Update staking amount
        let mut staking: Map<Address, i128> = env.storage().instance()
            .get(&symbol!("staking"))
            .unwrap_or(Map::new(&env));

        let current_stake = staking.get(user).unwrap_or(0);
        require!(current_stake >= amount, "Insufficient staked amount");

        staking.set(user, current_stake - amount);
        env.storage().instance().set(&symbol!("staking"), &staking);

        // Transfer tokens back to user
        let token_client = token::Client::new(&env, &env.current_contract_address());
        token_client.transfer(&env.current_contract_address(), &user, &amount);
    }

    /// Get user's staked amount
    pub fn get_staked_amount(env: Env, user: Address) -> i128 {
        let staking: Map<Address, i128> = env.storage().instance()
            .get(&symbol!("staking"))
            .unwrap_or(Map::new(&env));
        staking.get(user).unwrap_or(0)
    }

    /// Mint new tokens (admin only)
    ///
    /// # Arguments
    /// * `to` - Address to mint tokens to
    /// * `amount` - Amount to mint
    pub fn mint(env: Env, to: Address, amount: i128) {
        let admin = Self::get_admin(env.clone());
        require!(env.current_contract_address() == admin, "Admin only");

        let token_client = token::Client::new(&env, &env.current_contract_address());
        token_client.mint(&to, &amount);
    }

    /// Get tier thresholds
    pub fn get_tier_thresholds(env: Env) -> (i128, i128, i128) {
        let bronze = env.storage().instance()
            .get(&symbol!("bronze_tier"))
            .unwrap_or(BRONZE_TIER);
        let silver = env.storage().instance()
            .get(&symbol!("silver_tier"))
            .unwrap_or(SILVER_TIER);
        let gold = env.storage().instance()
            .get(&symbol!("gold_tier"))
            .unwrap_or(GOLD_TIER);

        (bronze, silver, gold)
    }

    /// Get total supply (delegates to token contract)
    pub fn total_supply(env: Env) -> i128 {
        let token_client = token::Client::new(&env, &env.current_contract_address());
        token_client.total_supply()
    }

    /// Get balance of an address (delegates to token contract)
    pub fn balance(env: Env, address: Address) -> i128 {
        let token_client = token::Client::new(&env, &env.current_contract_address());
        token_client.balance(&address)
    }

    /// Check if this contract is the admin (useful for access control in other contracts)
    pub fn is_admin(env: Env, address: Address) -> bool {
        let admin = Self::get_admin(env);
        address == admin
    }
}

// Utility functions
fn require<T: Into<bool>>(condition: T, message: &str) {
    if !condition.into() {
        panic!("{}", message);
    }
}