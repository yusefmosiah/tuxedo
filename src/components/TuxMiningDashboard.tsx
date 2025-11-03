/**
 * Legacy Tux Mining Dashboard - Agent-First Architecture
 *
 * Placeholder component for backward compatibility
 * TUX farming has been removed in favor of agent-first architecture
 */

import React from 'react';

export const TuxMiningDashboard: React.FC = () => {
  return (
    <div style={{
      padding: '20px',
      textAlign: 'center',
      backgroundColor: 'var(--color-bg-surface)',
      border: '1px solid var(--color-border)',
      borderRadius: 'var(--border-radius-lg)',
      margin: '20px 0'
    }}>
      <h3>🤖 Agent-First Architecture</h3>
      <p>TUX mining functionality has been removed.</p>
      <p>The system now uses AI agents that manage their own accounts autonomously.</p>
      <p>Use the chat interface to interact with Stellar DeFi protocols.</p>
    </div>
  );
};