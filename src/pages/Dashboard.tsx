import React, { useEffect } from "react";
import { Heading, Card, Content } from "@stellar/design-system";
import { useBlendPools } from "../hooks/useBlendPools";
import PoolsDashboard from "../components/dashboard/PoolsDashboard";
import { TuxMiningDashboard } from "../components/TuxMiningDashboard";

const Dashboard: React.FC = () => {
  const { pools, isLoading, error, refetch } = useBlendPools();

  useEffect(() => {
    // Only refetch when the page becomes visible again (user returns to tab)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        refetch();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [refetch]);

  if (error) {
    return (
      <div style={{ padding: "24px" }}>
        <Heading size="md">Dashboard Error</Heading>
        <Content>
          <p>Error loading pool data: {error}</p>
        </Content>
      </div>
    );
  }

  return (
    <div style={{ padding: "24px" }}>
      <Heading size="lg" spacing="md">
        📊 DeFindex Dashboard
      </Heading>

      {/* Tux Mining Section */}
      <Card style={{ marginBottom: "24px" }}>
        <Content>
          <TuxMiningDashboard />
        </Content>
      </Card>

      {/* Pools Section */}
      <Card>
        <Content>
          <PoolsDashboard
            pools={pools}
            isLoading={isLoading}
            onRefresh={refetch}
          />
        </Content>
      </Card>
    </div>
  );
};

export default Dashboard;