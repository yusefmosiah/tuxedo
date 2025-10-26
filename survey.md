# EasyA x Stellar Harvard Hackathon Submission

## Project Information

**Project Name:** Tuxedo

**Emails of all team members:** yusefnathanson@me.com

**Link to team's tweet announcing project:** [To be completed by team]

**Twitter handles of all team members:** [To be completed by team]

**Link to LinkedIn post about hackathon:** [To be completed by team]

**App Store review status:** Yep everyone on my team's now added their reviews!

## Project Description

**Short description (150 characters):**
Offers conversational AI agent to help crypto users easily discover and interact with Blend Protocol yield farming with natural language interface

**College/Employer:** [To be completed by team]

**Track:** Track 1 (Treat) — Infinite Cauldron: Open Innovation

**Full description:**
Tuxedo is a conversational AI agent that makes yield farming accessible and educational on Stellar's Blend Protocol. Our system features a fully operational AI agent with 6 integrated Stellar tools that can understand natural language queries and execute complex DeFi operations. Users can simply ask questions like "What pools are available?" or "Help me create a position in the USDC pool" and Tuxedo will handle the technical complexity. The system includes a React + TypeScript frontend with real-time chat interface and a FastAPI Python backend powered by LangChain and OpenAI. Tuxedo transforms the intimidating world of DeFi into an approachable, educational experience suitable for both beginners and experienced users.

**Technical explanation:**
Tuxedo uses a modern full-stack architecture with React 19 + TypeScript frontend and FastAPI Python backend. The AI agent leverages LangChain v2+ with OpenAI's gpt-oss 120b model for multi-step reasoning and tool selection. We've implemented 6 comprehensive Stellar tools using Stellar SDK 13.1.0+: Account Manager, Market Data, Trading, Trustline Manager, Utilities, and Soroban smart contracts. The frontend uses Stellar Design System + Stellar Wallets Kit for wallet integration, and TanStack React Query for data management. Key Stellar features we leveraged include Soroban smart contracts for Blend Protocol integration, Horizon API for market data and account operations, and the testnet Friendbot for easy account funding. Stellar's fast transaction times and low fees make this conversational DeFi experience uniquely possible compared to other blockchains.

**Address of deployed contract:**
TUX Token (Stellar Asset): TUX:GA23UZT2AL4WA4GONJQD75C3QYRBS3XFW6ZHZUBHDDKOQI22LKHLUX3H (Testnet)
TUX Token Contract: CD3SYXBQWYEQ6J2J5XC4V7MMPZQK3YYKQI6OMZAJ5U2C6XQ3U2Z7Z7Y (Testnet)

**URL to demo site:** [To be completed - likely localhost:5173 for demo]

**Link to slides:** [To be completed by team]

**LLMs used:** OpenAI gpt-oss 120b via Redpill AI API

**Where we struggled the most:** Managing the complexity of Stellar's testnet configuration and hardcoded values throughout the codebase. Creating a centralized configuration system that could handle the 13+ categories of hardcoded testnet values while maintaining the AI agent's functionality was challenging. Also, implementing proper error handling for the multi-step AI reasoning process required significant iteration.

**Funding application status:** Yep! Can't wait!

**Work originality confirmation:** Yes

**EasyA startup pledge:** No

**GitHub repo:** https://github.com/[username]/tuxedo [To be completed with actual repo]

**Submission requirements confirmation:** Yes! 100%

---

## Notes for Team

- [ ] Complete team member emails
- [ ] Create and share project announcement tweet tagging @EasyA_App and @StellarOrg
- [ ] Add team member Twitter handles
- [ ] Create LinkedIn post about hackathon experience tagging @EasyA
- [ ] Ensure everyone has rated EasyA app 5 stars with reviews
- [ ] Add college/employer information
- [ ] Prepare demo site URL (likely running locally)
- [ ] Complete presentation slides using provided Canva template
- [ ] Confirm actual GitHub repository URL
- [ ] Verify all submission requirements are met before deadline