import React, { useState } from 'react';
import { Button, Text, TabGroup, Tab } from "@stellar/design-system";
import { useBlendPools } from "../../hooks/useBlendPools";
import { useWallet } from "../../hooks/useWallet";
import { PoolCard } from "./PoolCard";
import { TuxFarmingDashboard } from "../farming/TuxFarmingDashboard";

interface CompleteDashboardProps {
  className?: string;
}

/**
 * CompleteDashboard - Unified dashboard for Blend pools and TUX farming
 *
 * Features:
 * - Tabbed interface for Blend and TUX features
 * - Blend pool management
 * - TUX yield farming dashboard
 * - Wallet integration
 * - Summary statistics across both platforms
 */
export const CompleteDashboard: React.FC<CompleteDashboardProps> = ({ className }) => {
  const { pools, loading: blendLoading, error: blendError, refetch } = useBlendPools();
  const { walletAddress } = useWallet();
  const [activeTab, setActiveTab] = useState<"blend" | "farming">("blend");

  // Calculate Blend stats
  const totalPools = pools.length;
  const totalReserves = pools.reduce((sum, pool) => sum + pool.totalReserves, 0);
  const activePools = pools.filter((p) => p.status === "active").length;

  const tabs = [
    {
      id: "blend" as const,
      title: "Blend Pools",
      component: (
        <div className="space-y-6">
          {/* Blend Header */}
          <div className="card p-6 bg-surface border border-border">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-semibold text-text-primary mb-2">
                  Blend Pools Dashboard
                </h1>
                <p className="text-text-secondary">
                  Lend and borrow assets through Stellar's premier liquidity protocol
                </p>
              </div>
              <Button onClick={refetch} variant="secondary" size="sm">
                Refresh
              </Button>
            </div>
          </div>

          {/* Blend Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card p-4 bg-surface border border-border">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{totalPools}</p>
                <p className="text-sm text-text-secondary">Total Pools</p>
              </div>
            </div>
            <div className="card p-4 bg-surface border border-border">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{activePools}</p>
                <p className="text-sm text-text-secondary">Active Pools</p>
              </div>
            </div>
            <div className="card p-4 bg-surface border border-border">
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">
                  ${totalReserves.toLocaleString()}
                </p>
                <p className="text-sm text-text-secondary">Total Reserves</p>
              </div>
            </div>
          </div>

          {/* Blend Pools List */}
          {blendLoading ? (
            <div className="flex items-center justify-center p-8">
              <Text>Loading Blend pools...</Text>
              <Loader size="sm" />
            </div>
          ) : blendError ? (
            <div className="card p-4 bg-red-50 border border-red-200">
              <Text>Error loading pools: {blendError}</Text>
              <Button onClick={refetch} variant="secondary" size="sm">
                Retry
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {pools.map((pool) => (
                <PoolCard key={pool.address} pool={pool} />
              ))}
            </div>
          )}
        </div>
      ),
    },
    {
      id: "farming" as const,
      title: "TUX Farming",
      component: (
        <div className="space-y-6">
          {/* TUX Farming Header */}
          <div className="card p-6 bg-surface border border-border">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-semibold text-text-primary mb-2">
                  TUX Yield Farming
                </h1>
                <p className="text-text-secondary">
                  Earn TUX tokens by providing liquidity to Stellar DeFi protocols
                </p>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-yellow-500 to-orange-600 flex items-center justify-center">
                  <span className="text-white font-bold text-xs">TUX</span>
                </div>
                {walletAddress && (
                  <Text variant="body2" className="text-text-tertiary">
                    Connected: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
                  </Text>
                )}
              </div>
            </div>
          </div>

          {/* TUX Farming Dashboard */}
          <TuxFarmingDashboard walletAddress={walletAddress} />
        </div>
      ),
    },
  ];

  return (
    <div className={`max-w-7xl mx-auto p-4 ${className}`}>
      {/* Main Header */}
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-text-primary mb-2">
          Tuxedo DeFi Hub
        </h1>
        <p className="text-lg text-text-secondary max-w-2xl mx-auto">
          Your gateway to Stellar DeFi. Lend, borrow, and farm yields across Blend and TUX protocols.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-8">
        <TabGroup
          activeId={activeTab}
          onChange={(tabId) => setActiveTab(tabId as "blend" | "farming")}
        >
          {tabs.map((tab) => (
            <Tab key={tab.id} id={tab.id}>
              {tab.title}
            </Tab>
          ))}
        </TabGroup>
      </div>

      {/* Tab Content */}
      <div>
        {tabs.find((tab) => tab.id === activeTab)?.component}
      </div>

      {/* Wallet Not Connected Alert */}
      {!walletAddress && (
        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-yellow-800">Connect Your Wallet</h3>
              <p className="text-yellow-600 text-sm mt-1">
                Connect your Stellar wallet to see your positions and manage your investments.
              </p>
            </div>
            <Button size="sm">Connect Wallet</Button>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-12 text-center text-text-tertiary text-sm">
        <p>
          Powered by Stellar Network • TUX tokens • Blend Protocol
        </p>
        <p className="mt-2">
          Testnet Environment • For demonstration purposes only
        </p>
      </div>
    </div>
  );
};