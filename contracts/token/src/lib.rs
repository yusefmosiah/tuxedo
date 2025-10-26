#![no_std]

use soroban_sdk::{
    contract, contracterror, contractimpl, Address, Env, String, Symbol,
    token::TokenInterface, symbol_short,
};
use stellar_tokens::fungible::Base;

// ============ Constants ============
const OWNER: Symbol = symbol_short!("OWNER");

// ============ Errors ============
#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum TokenError {
    AlreadyInitialized = 1,
    Unauthorized = 2,
    InsufficientBalance = 3,
    InvalidAmount = 4,
}

// ============ TUX Token Contract ============
#[contract]
pub struct TuxToken;

#[contractimpl]
impl TuxToken {
    /// Initialize the TUX token contract
    ///
    /// Arguments:
    /// - admin: Admin address that can mint tokens
    /// - initial_supply: Initial token supply to mint
    pub fn initialize(env: Env, admin: Address, initial_supply: i128) -> Result<(), TokenError> {
        // Check if already initialized
        if env.storage().instance().has(&OWNER) {
            return Err(TokenError::AlreadyInitialized);
        }

        // Validate inputs
        if initial_supply < 0 {
            return Err(TokenError::InvalidAmount);
        }

        // Set token metadata (TUX token with 7 decimals like Stellar assets)
        Base::set_metadata(
            &env,
            7,
            String::from_str(&env, "Tuxedo Token"),
            String::from_str(&env, "TUX")
        );

        // Mint initial supply to admin
        Base::mint(&env, &admin, initial_supply);

        // Set owner
        env.storage().instance().set(&OWNER, &admin);

        // Emit initialization event
        env.events().publish(
            (symbol_short!("tkn"), symbol_short!("init")),
            (admin, initial_supply),
        );

        Ok(())
    }

    /// Mint new tokens (admin only)
    pub fn mint(env: Env, admin: Address, to: Address, amount: i128) -> Result<(), TokenError> {
        // Verify admin authorization
        let owner: Address = env.storage().instance().get(&OWNER).unwrap();
        if admin != owner {
            return Err(TokenError::Unauthorized);
        }

        admin.require_auth();

        // Validate amount
        if amount <= 0 {
            return Err(TokenError::InvalidAmount);
        }

        // Mint tokens
        Base::mint(&env, &to, amount);

        // Emit mint event
        env.events().publish(
            (symbol_short!("tkn"), symbol_short!("mint")),
            (admin, to, amount),
        );

        Ok(())
    }

    
    /// Get contract admin
    pub fn get_admin(env: Env) -> Address {
        env.storage().instance().get(&OWNER).unwrap()
    }
}

// ============ TokenInterface Implementation ============
#[contractimpl]
impl TokenInterface for TuxToken {
    fn allowance(env: Env, from: Address, spender: Address) -> i128 {
        Base::allowance(&env, &from, &spender)
    }

    fn approve(env: Env, from: Address, spender: Address, amount: i128, live_until_ledger: u32) {
        Base::approve(&env, &from, &spender, amount, live_until_ledger);
    }

    fn balance(env: Env, id: Address) -> i128 {
        Base::balance(&env, &id)
    }

    fn transfer(env: Env, from: Address, to: Address, amount: i128) {
        Base::transfer(&env, &from, &to, amount);
    }

    fn transfer_from(env: Env, spender: Address, from: Address, to: Address, amount: i128) {
        Base::transfer_from(&env, &spender, &from, &to, amount);
    }

    fn burn(env: Env, from: Address, amount: i128) {
        Base::burn(&env, &from, amount);
    }

    fn burn_from(env: Env, spender: Address, from: Address, amount: i128) {
        Base::burn_from(&env, &spender, &from, amount);
    }

    fn decimals(env: Env) -> u32 {
        Base::decimals(&env)
    }

    fn name(env: Env) -> String {
        Base::name(&env)
    }

    fn symbol(env: Env) -> String {
        Base::symbol(&env)
    }
}

// ============ Test Suite ============
#[cfg(test)]
mod tests {
    use super::*;
    use soroban_sdk::testutils::{Address as _, Ledger as _};

    #[test]
    fn test_initialize() {
        let env = Env::default();
        let admin = Address::generate(&env);

        let initial_supply = 100_000_000i128 * 10_000_000i128; // 100M TUX with 7 decimals

        TuxToken::initialize(env.clone(), admin.clone(), initial_supply).unwrap();

        assert_eq!(TuxToken::name(env.clone()), "Tuxedo Token");
        assert_eq!(TuxToken::symbol(env.clone()), "TUX");
        assert_eq!(TuxToken::decimals(env.clone()), 7);
        assert_eq!(TuxToken::balance(env.clone(), admin.clone()), initial_supply);
        assert_eq!(TuxToken::get_admin(env.clone()), admin);
    }

    #[test]
    fn test_transfer() {
        let env = Env::default();
        let admin = Address::generate(&env);
        let user = Address::generate(&env);

        let initial_supply = 100_000_000i128 * 10_000_000i128;
        let transfer_amount = 1_000i128 * 10_000_000i128; // 1,000 TUX

        TuxToken::initialize(env.clone(), admin.clone(), initial_supply).unwrap();

        // Transfer from admin to user
        TuxToken::transfer(env.clone(), admin.clone(), user.clone(), transfer_amount);

        assert_eq!(TuxToken::balance(env.clone(), admin.clone()), initial_supply - transfer_amount);
        assert_eq!(TuxToken::balance(env.clone(), user.clone()), transfer_amount);
    }

    #[test]
    fn test_mint() {
        let env = Env::default();
        let admin = Address::generate(&env);
        let user = Address::generate(&env);

        let initial_supply = 50_000_000i128 * 10_000_000i128;
        let mint_amount = 10_000i128 * 10_000_000i128; // 10,000 TUX

        TuxToken::initialize(env.clone(), admin.clone(), initial_supply).unwrap();

        // Mint additional tokens
        TuxToken::mint(env.clone(), admin.clone(), user.clone(), mint_amount).unwrap();

        assert_eq!(TuxToken::balance(env.clone(), user.clone()), mint_amount);
    }

    #[test]
    fn test_burn() {
        let env = Env::default();
        let admin = Address::generate(&env);

        let initial_supply = 100_000_000i128 * 10_000_000i128;
        let burn_amount = 10_000i128 * 10_000_000i128; // 10,000 TUX

        TuxToken::initialize(env.clone(), admin.clone(), initial_supply).unwrap();

        // Burn tokens
        TuxToken::burn(env.clone(), admin.clone(), burn_amount).unwrap();

        assert_eq!(TuxToken::balance(env.clone(), admin.clone()), initial_supply - burn_amount);
    }
}