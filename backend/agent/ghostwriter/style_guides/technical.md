# Technical Style Guide

## Target Audience
Software engineers, blockchain developers, technical stakeholders

## Tone
- Professional and precise
- Technical terminology encouraged
- Assume reader has technical background
- Direct and efficient communication

## Language Characteristics
- **Voice**: Active voice preferred ("The protocol executes transactions" vs "Transactions are executed")
- **Complexity**: Technical jargon acceptable and encouraged
- **Precision**: Use exact numbers and specific technical terms
- **Examples**: Include code snippets, technical diagrams, API references

## Formatting
- **Headings**: Use descriptive technical headings (## Architecture Overview)
- **Lists**: Use for technical specifications
- **Code blocks**: Mark up technical terms, contract addresses, function names
- **Citations**: Inline numerical format [1][2]

## Vocabulary
- Prefer: "implementation", "protocol", "smart contract", "transaction throughput"
- Avoid: "thing", "stuff", "basically", casual expressions

## Sentence Structure
- Medium length (15-25 words average)
- Technical subordinate clauses acceptable
- Prioritize clarity over simplicity
- Use technical abbreviations (TVL, APY, TPS) after first definition

## Example

**Good Technical Style:**
"The Blend Capital lending protocol implements a liquidation mechanism with a 75% LTV threshold. When collateral value drops below this threshold, the smart contract automatically triggers liquidation via the backstop module [1]. The protocol achieves approximately 1,000 transactions per second (TPS) on the Stellar network [2]."

**Incorrect (too casual):**
"Blend is pretty cool because it basically liquidates your stuff if it drops too low. It's super fast on Stellar."
