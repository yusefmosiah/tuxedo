/**
 * Parse and extract embedded Stellar transaction data from AI responses
 *
 * Transaction Format:
 * [STELLAR_TX]{"xdr":"...","description":"...","network":"testnet"}[/STELLAR_TX]
 */

export interface EmbeddedTransaction {
  xdr: string;
  description: string;
  network?: string;
  vault_address?: string;
  amount?: number;
  estimated_shares?: string;
  note?: string;
}

export interface ParsedMessage {
  beforeTx: string;
  transaction: EmbeddedTransaction | null;
  afterTx: string;
}

const TX_REGEX = /\[STELLAR_TX\](.*?)\[\/STELLAR_TX\]/s;

/**
 * Parse a message to extract embedded transaction data
 */
export function parseMessageForTransaction(content: string | undefined): ParsedMessage {
  // Handle undefined or null content
  if (!content) {
    return {
      beforeTx: '',
      transaction: null,
      afterTx: '',
    };
  }

  const match = content.match(TX_REGEX);

  if (!match) {
    return {
      beforeTx: content,
      transaction: null,
      afterTx: '',
    };
  }

  try {
    const txJson = match[1].trim();
    const transaction = JSON.parse(txJson) as EmbeddedTransaction;

    // Split the message into before and after the transaction
    const parts = content.split(TX_REGEX);
    const beforeTx = parts[0]?.trim() || '';
    const afterTx = parts[2]?.trim() || '';

    return {
      beforeTx,
      transaction,
      afterTx,
    };
  } catch (error) {
    console.error('Failed to parse embedded transaction:', error);
    return {
      beforeTx: content,
      transaction: null,
      afterTx: '',
    };
  }
}

/**
 * Check if a message contains an embedded transaction
 */
export function hasEmbeddedTransaction(content: string | undefined): boolean {
  if (!content) return false;
  return TX_REGEX.test(content);
}
