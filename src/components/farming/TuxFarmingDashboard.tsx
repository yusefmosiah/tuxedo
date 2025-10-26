import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, TrendingUp, Coins, Clock, CheckCircle } from 'lucide-react';
import { useTuxFarming } from '../../hooks/useTuxFarming';

interface TuxFarmingDashboardProps {
  className?: string;
}

export const TuxFarmingDashboard: React.FC<TuxFarmingDashboardProps> = ({
  className
}) => {
  const { overview, userPositions, loading, error, refetch, getPoolDetails } = useTuxFarming();
  const [selectedPool, setSelectedPool] = useState<string | null>(null);

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  };

  const formatLargeNumber = (num: number): string => {
    if (num >= 1e9) {
      return `${(num / 1e9).toFixed(2)}B`;
    } else if (num >= 1e6) {
      return `${(num / 1e6).toFixed(2)}M`;
    } else if (num >= 1e3) {
      return `${(num / 1e3).toFixed(2)}K`;
    }
    return num.toString();
  };

  const handlePoolSelect = async (poolId: string) => {
    if (selectedPool === poolId) {
      setSelectedPool(null);
      return;
    }

    try {
      setSelectedPool(poolId);
      // Could fetch more detailed pool info here if needed
      const details = await getPoolDetails(poolId);
      console.log('Pool details:', details);
    } catch (err) {
      console.error('Error fetching pool details:', err);
    }
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading TUX farming data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className={className}>
        <AlertDescription>
          Error loading farming data: {error}
          <Button size="sm" variant="outline" className="ml-2" onClick={refetch}>
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  if (!overview) {
    return (
      <Alert className={className}>
        <AlertDescription>
          No farming data available. Please check back later.
          <Button size="sm" variant="outline" className="ml-2" onClick={refetch}>
            Refresh
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Token Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Coins className="h-5 w-5" />
            TUX Token Information
          </CardTitle>
          <CardDescription>
            Native utility token for Tuxedo ecosystem rewards
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Name</p>
              <p className="font-medium">{overview.token_info.name}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Symbol</p>
              <p className="font-medium">{overview.token_info.symbol}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Supply</p>
              <p className="font-medium">{formatLargeNumber(overview.token_info.total_supply)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Contract</p>
              <p className="font-medium text-xs truncate">{overview.token_info.contract_address}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* User Summary */}
      {userPositions && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Your Farming Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {userPositions.formatted_total_pending}
                </p>
                <p className="text-sm text-muted-foreground">Pending Rewards</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">
                  {userPositions.active_positions}
                </p>
                <p className="text-sm text-muted-foreground">Active Positions</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">
                  {overview.pools.filter(p => p.is_active).length}
                </p>
                <p className="text-sm text-muted-foreground">Available Pools</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Farming Pools */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Coins className="h-5 w-5" />
            Farming Pools
          </CardTitle>
          <CardDescription>
            Stake tokens to earn TUX rewards
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {overview.pools.map((pool) => (
              <div
                key={pool.pool_id}
                className={`border rounded-lg p-4 transition-colors cursor-pointer ${
                  selectedPool === pool.pool_id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
                onClick={() => handlePoolSelect(pool.pool_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                      <span className="text-white font-bold text-xs">
                        {pool.pool_id.substring(0, 2)}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-semibold">{pool.pool_id} Pool</h3>
                      <p className="text-sm text-muted-foreground">
                        Stake {pool.staking_token} to earn TUX
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-semibold text-green-600">{formatNumber(pool.apy)}%</p>
                      <p className="text-xs text-muted-foreground">APY</p>
                    </div>
                    <Badge variant={pool.is_active ? "default" : "secondary"}>
                      {pool.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </div>

                {userPositions && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Your Stake</p>
                        <p className="font-medium">
                          {formatNumber(userPositions.positions.find(p => p.pool_id === pool.pool_id)?.amount_staked || 0)}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Pending Rewards</p>
                        <p className="font-medium text-green-600">
                          {userPositions.positions.find(p => p.pool_id === pool.pool_id)?.formatted_pending_rewards || '0.00 TUX'}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Total Staked</p>
                        <p className="font-medium">{formatLargeNumber(pool.total_staked)}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {userPositions.positions.find(p => p.pool_id === pool.pool_id)?.amount_staked ? (
                          <Button size="sm" variant="outline">
                            Manage
                          </Button>
                        ) : (
                          <Button size="sm">
                            Stake
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {selectedPool === pool.pool_id && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Staking Token</p>
                        <p className="font-medium">{pool.staking_token}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Pool Status</p>
                        <div className="flex items-center gap-1">
                          {pool.is_active ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : (
                            <Clock className="h-4 w-4 text-yellow-500" />
                          )}
                          <span className="font-medium">
                            {pool.is_active ? 'Accepting deposits' : 'Paused'}
                          </span>
                        </div>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Total Value Locked</p>
                        <p className="font-medium">{formatLargeNumber(pool.total_staked)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {!userPositions && (
        <Alert>
          <AlertDescription>
            Connect your wallet to see your farming positions and manage your stakes.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};