#![no_std]

use soroban_sdk::{
    contract, contracterror, contractimpl, Address, Env, Symbol, symbol_short,
};

// ============ Constants ============
const OWNER: Symbol = symbol_short!("OWNER");
const TUX_TOKEN: Symbol = symbol_short!("TUX_TKN");

// ============ Errors ============
#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum FarmingError {
    AlreadyInitialized = 1,
    NotAuthorized = 2,
    PoolNotFound = 3,
    InvalidAmount = 4,
    InsufficientBalance = 5,
    TokenError = 6,
}

// ============ TUX Farming Contract ============
#[contract]
pub struct TuxFarming;

#[contractimpl]
impl TuxFarming {
    /// Initialize the farming contract
    pub fn initialize(
        env: Env,
        admin: Address,
        tux_token: Address,
    ) -> Result<(), FarmingError> {
        // Check if already initialized
        if env.storage().instance().has(&OWNER) {
            return Err(FarmingError::AlreadyInitialized);
        }

        // Set initial state
        env.storage().instance().set(&OWNER, &admin);
        env.storage().instance().set(&TUX_TOKEN, &tux_token);

        // Emit initialization event
        env.events().publish(
            (symbol_short!("farm"), symbol_short!("init")),
            (admin, tux_token),
        );

        Ok(())
    }

    /// Add a new staking pool (admin only)
    pub fn add_pool(
        env: Env,
        admin: Address,
        pool_id: Symbol,
        staking_token: Address,
    ) -> Result<(), FarmingError> {
        // Verify admin authorization
        let owner: Address = env.storage().instance().get(&OWNER).unwrap();
        if admin != owner {
            return Err(FarmingError::NotAuthorized);
        }

        admin.require_auth();

        // Store pool token address
        env.storage().instance().set(&pool_id, &staking_token);

        // Emit pool added event
        env.events().publish(
            (symbol_short!("farm"), symbol_short!("pool")),
            (pool_id, staking_token),
        );

        Ok(())
    }

    /// Stake tokens in a pool
    pub fn stake(
        env: Env,
        user: Address,
        pool_id: Symbol,
        amount: i128,
    ) -> Result<(), FarmingError> {
        user.require_auth();

        // Validate amount
        if amount <= 0 {
            return Err(FarmingError::InvalidAmount);
        }

        // Get pool token
        let staking_token: Address = env.storage().instance().get(&pool_id).unwrap_or_else(|| {
            // Return a dummy address and handle the error below
            Address::from_str(&env, "GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        });

        // Verify pool exists by checking if it's the dummy address
        let dummy_addr = Address::from_str(&env, "GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
        if staking_token == dummy_addr {
            return Err(FarmingError::PoolNotFound);
        }

        // Transfer staking tokens from user to contract
        let token_client = soroban_sdk::token::TokenClient::new(&env, &staking_token);
        token_client.transfer(&user, &env.current_contract_address(), &amount);

        // Update user stake (simple counter)
        let stake_key = (user.clone(), pool_id.clone());
        let current_stake: i128 = env.storage().persistent().get(&stake_key).unwrap_or(0);
        env.storage().persistent().set(&stake_key, &(current_stake + amount));

        // Emit stake event
        env.events().publish(
            (symbol_short!("farm"), symbol_short!("stake")),
            (user, pool_id, amount),
        );

        Ok(())
    }

    /// Unstake tokens from a pool
    pub fn unstake(
        env: Env,
        user: Address,
        pool_id: Symbol,
        amount: i128,
    ) -> Result<(), FarmingError> {
        user.require_auth();

        // Validate amount
        if amount <= 0 {
            return Err(FarmingError::InvalidAmount);
        }

        // Get user stake
        let stake_key = (user.clone(), pool_id.clone());
        let current_stake: i128 = env.storage().persistent().get(&stake_key).unwrap_or(0);

        if current_stake < amount {
            return Err(FarmingError::InsufficientBalance);
        }

        // Get pool token
        let staking_token: Address = env.storage().instance().get(&pool_id).unwrap_or_else(|| {
            // Return a dummy address and handle the error below
            Address::from_str(&env, "GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        });

        // Verify pool exists by checking if it's the dummy address
        let dummy_addr = Address::from_str(&env, "GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
        if staking_token == dummy_addr {
            return Err(FarmingError::PoolNotFound);
        }

        // Update user stake
        let new_stake = current_stake - amount;
        if new_stake == 0 {
            env.storage().persistent().remove(&stake_key);
        } else {
            env.storage().persistent().set(&stake_key, &new_stake);
        }

        // Transfer staking tokens back to user
        let token_client = soroban_sdk::token::TokenClient::new(&env, &staking_token);
        token_client.transfer(&env.current_contract_address(), &user, &amount);

        // Emit unstake event
        env.events().publish(
            (symbol_short!("farm"), symbol_short!("unstake")),
            (user, pool_id, amount),
        );

        Ok(())
    }

    /// Mint TUX rewards (admin only, simplified reward distribution)
    pub fn mint_rewards(
        env: Env,
        admin: Address,
        to: Address,
        amount: i128,
    ) -> Result<(), FarmingError> {
        // Verify admin authorization
        let owner: Address = env.storage().instance().get(&OWNER).unwrap();
        if admin != owner {
            return Err(FarmingError::NotAuthorized);
        }

        admin.require_auth();

        // Validate amount
        if amount <= 0 {
            return Err(FarmingError::InvalidAmount);
        }

        // Transfer TUX tokens (contract must have TUX balance)
        let tux_token: Address = env.storage().instance().get(&TUX_TOKEN).unwrap();
        let token_client = soroban_sdk::token::TokenClient::new(&env, &tux_token);
        token_client.transfer(&env.current_contract_address(), &to, &amount);

        // Emit reward event
        env.events().publish(
            (symbol_short!("farm"), symbol_short!("reward")),
            (admin, to, amount),
        );

        Ok(())
    }

    /// Get pool token address
    pub fn get_pool_token(env: Env, pool_id: Symbol) -> Result<Address, FarmingError> {
        env.storage()
            .instance()
            .get(&pool_id)
            .ok_or(FarmingError::PoolNotFound)
    }

    /// Get user stake amount
    pub fn get_user_stake(
        env: Env,
        user: Address,
        pool_id: Symbol,
    ) -> i128 {
        let stake_key = (user, pool_id);
        env.storage()
            .persistent()
            .get(&stake_key)
            .unwrap_or(0)
    }

    /// Get contract admin
    pub fn get_admin(env: Env) -> Address {
        env.storage().instance().get(&OWNER).unwrap()
    }

    /// Get TUX token address
    pub fn get_tux_token(env: Env) -> Address {
        env.storage().instance().get(&TUX_TOKEN).unwrap()
    }
}