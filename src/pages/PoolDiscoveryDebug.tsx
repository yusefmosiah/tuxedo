import { useState } from "react";
import { generatePoolTokenReport, logPoolStats, discoverAllPools } from "../utils/poolDiscovery";

/**
 * Debug page to exhaustively discover all Blend pools and tokens on testnet
 */
export function PoolDiscoveryDebug() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<{
    pools: string[];
    tokens: string[];
    reports: any[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunDiscovery = async () => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      console.clear();
      console.log("🚀 Starting pool discovery...\n");

      // Run full analysis
      const discovery = await discoverAllPools();
      const reports = await generatePoolTokenReport();
      await logPoolStats();

      // Extract tokens from reports
      const allTokens = new Set<string>();
      reports.forEach(report => {
        report.tokens.forEach((token: any) => {
          allTokens.add(token.address);
        });
      });

      setResults({
        pools: discovery.allPoolsUnique,
        tokens: Array.from(allTokens),
        reports,
      });

      console.log("\n✅ Discovery complete! Check the page below for results.");
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error("❌ Discovery failed:", err);
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "monospace" }}>
      <h1>🔍 Pool Discovery Debug</h1>

      <button
        onClick={handleRunDiscovery}
        disabled={isLoading}
        style={{
          padding: "10px 20px",
          fontSize: "16px",
          backgroundColor: "#6366f1",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: isLoading ? "not-allowed" : "pointer",
          opacity: isLoading ? 0.5 : 1,
        }}
      >
        {isLoading ? "⏳ Discovering..." : "🚀 Run Discovery"}
      </button>

      {error && (
        <div
          style={{
            marginTop: "20px",
            padding: "15px",
            backgroundColor: "#fee",
            border: "1px solid #f00",
            borderRadius: "4px",
            color: "#c00",
          }}
        >
          <strong>❌ Error:</strong> {error}
          <p style={{ fontSize: "12px", marginTop: "10px" }}>
            Check browser console for detailed logs (F12)
          </p>
        </div>
      )}

      {results && (
        <div style={{ marginTop: "20px" }}>
          <h2>📊 Results</h2>

          <section style={{ marginBottom: "30px" }}>
            <h3>🏊 Pools Found: {results.pools.length}</h3>
            {results.pools.length === 0 ? (
              <p style={{ color: "#999" }}>No pools discovered</p>
            ) : (
              <ul style={{ paddingLeft: "20px" }}>
                {results.pools.map((pool, i) => {
                  const report = results.reports.find(r => r.poolAddress === pool);
                  return (
                    <li key={pool} style={{ marginBottom: "15px" }}>
                      <div>
                        <strong>Pool {i + 1}:</strong> {pool}
                      </div>
                      {report && (
                        <div style={{ marginLeft: "20px", marginTop: "5px", fontSize: "14px" }}>
                          <div>
                            <strong>Name:</strong> {report.poolName}
                          </div>
                          <div>
                            <strong>Tokens ({report.tokenCount}):</strong>
                          </div>
                          <ul style={{ fontSize: "12px", paddingLeft: "20px", marginTop: "5px" }}>
                            {report.tokens.map((token: any) => (
                              <li key={token.address} style={{ fontFamily: "monospace", wordBreak: "break-all" }}>
                                {token.address}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </section>

          <section>
            <h3>💰 All Unique Tokens: {results.tokens.length}</h3>
            {results.tokens.length === 0 ? (
              <p style={{ color: "#999" }}>No tokens found</p>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "10px" }}>
                {results.tokens.map((token, i) => (
                  <div
                    key={token}
                    style={{
                      padding: "10px",
                      backgroundColor: "#f5f5f5",
                      borderRadius: "4px",
                      wordBreak: "break-all",
                      fontSize: "12px",
                      fontFamily: "monospace",
                    }}
                  >
                    <strong>{i + 1}.</strong> {token}
                  </div>
                ))}
              </div>
            )}
          </section>

          <section style={{ marginTop: "30px", padding: "15px", backgroundColor: "#eef", borderRadius: "4px" }}>
            <p style={{ margin: "0", fontSize: "12px", color: "#666" }}>
              💡 Check browser console (F12) for detailed logs about pool discovery process
            </p>
          </section>
        </div>
      )}
    </div>
  );
}

export default PoolDiscoveryDebug;
