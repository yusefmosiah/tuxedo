# Security Policy

The Choir protocol is designed with a multi-layered security architecture that prioritizes user sovereignty, data privacy, and asset protection. Our approach is grounded in the principle of least privilege and verifiable, hardware-level isolation.

## Core Security Pillars

### 1. User Sovereignty & Non-Custodial Vaults
*   **You Own Your Keys**: All DeFi vaults are non-custodial. Users hold shares representing their portion of a vault's assets. The protocol, and by extension the Choir team, never takes custody of user funds.
*   **Agent-Based Execution**: While AI agents can propose and execute DeFi strategies, they do so with keys managed in a secure enclave, and all operations are verifiable on-chain.

### 2. Privacy by Default
*   **Trusted Execution Environments (TEE)**: The core of our agentic architecture runs on the Phala Network, a decentralized cloud of Trusted Execution Environments. This ensures that user data, including multi-chain private keys (`keys.json`), preferences (`context.db`), and even the agent logic itself, is encrypted and isolated even from the underlying infrastructure.
*   **Anonymous Publishing**: All research is published anonymously, with authorship proven by cryptographic wallet signatures. This protects researchers from career risk while ensuring immutable attribution.
*   **Zero Personal Data**: We do not collect or store any personally identifiable information.

### 3. Secure Authentication
*   **Passkey Authentication**: We use WebAuthn (passkeys) for all user authentication. This provides phishing-resistant, biometric security without the need for traditional passwords or seed phrases.
*   **Cryptographic Identity**: All user identity is based on wallet signatures, not on personal data.

## Reporting a Vulnerability

We maintain an active security program and welcome contributions from independent security researchers. If you believe you have found a security vulnerability in the Choir protocol, please report it to us through one of the following channels:

*   **GitHub Security Advisories**: You can submit a report privately through GitHub's security advisory system.
*   **Email**: You can send a detailed report to `security@choir.chat`.

We are committed to working with researchers to verify and address any potential vulnerabilities. Bounties are available for critical, responsibly disclosed vulnerabilities.
