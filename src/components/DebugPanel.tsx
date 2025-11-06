/**
 * Debug Panel Component
 * Displays comprehensive debug logs from passkey authentication in the UI
 */
import { useState, useEffect } from "react";
import { debugLogs, clearDebugLogs } from "../services/passkeyAuth";

export function DebugPanel() {
  const [logs, setLogs] = useState<string[]>([...debugLogs]);
  const [isVisible, setIsVisible] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);

  // Update logs every 500ms
  useEffect(() => {
    const interval = setInterval(() => {
      setLogs([...debugLogs]);
    }, 500);

    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll) {
      const logsContainer = document.getElementById("debug-logs-container");
      if (logsContainer) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
      }
    }
  }, [logs, autoScroll]);

  const handleClear = () => {
    clearDebugLogs();
    setLogs([]);
  };

  const handleCopy = () => {
    const logsText = logs.join("\n");
    navigator.clipboard.writeText(logsText);
    alert("Debug logs copied to clipboard!");
  };

  const handleDownload = () => {
    const logsText = logs.join("\n");
    const blob = new Blob([logsText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `passkey-debug-${new Date().toISOString().replace(/:/g, "-")}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 z-50 px-4 py-2 bg-blue-600 text-white rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
      >
        🐛 Show Debug Logs ({logs.length})
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-[600px] max-w-[90vw] bg-gray-900 border border-gray-700 rounded-lg shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700 rounded-t-lg">
        <div className="flex items-center gap-2">
          <span className="text-white font-semibold">🐛 Debug Logs</span>
          <span className="text-gray-400 text-sm">({logs.length})</span>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1 text-xs text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="w-3 h-3"
            />
            Auto-scroll
          </label>
          <button
            onClick={handleCopy}
            className="px-2 py-1 text-xs bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors"
            title="Copy logs to clipboard"
          >
            📋 Copy
          </button>
          <button
            onClick={handleDownload}
            className="px-2 py-1 text-xs bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors"
            title="Download logs as file"
          >
            💾 Save
          </button>
          <button
            onClick={handleClear}
            className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            🗑️  Clear
          </button>
          <button
            onClick={() => setIsVisible(false)}
            className="px-2 py-1 text-xs bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Logs Container */}
      <div
        id="debug-logs-container"
        className="h-[400px] overflow-y-auto p-4 bg-black font-mono text-xs"
      >
        {logs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            No debug logs yet. Perform a passkey operation to see logs here.
          </div>
        ) : (
          logs.map((log, index) => {
            // Color code based on log type
            let logColor = "text-gray-300";
            if (log.includes("❌")) logColor = "text-red-400";
            else if (log.includes("✅")) logColor = "text-green-400";
            else if (log.includes("⚠️")) logColor = "text-yellow-400";
            else if (log.includes("📡")) logColor = "text-blue-400";
            else if (log.includes("🔍")) logColor = "text-purple-400";
            else if (log.includes("⏱️")) logColor = "text-cyan-400";

            return (
              <div
                key={index}
                className={`${logColor} mb-1 whitespace-pre-wrap break-all`}
              >
                {log}
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-800 border-t border-gray-700 rounded-b-lg text-xs text-gray-400">
        💡 Tip: Keep this open while testing passkey registration/login to diagnose issues
      </div>
    </div>
  );
}
