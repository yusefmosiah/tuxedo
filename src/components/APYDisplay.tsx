import React from "react";

interface APYDisplayProps {
  apy: number;
  showUnit?: boolean;
  size?: "small" | "medium" | "large";
}

/**
 * APYDisplay - Semantic APY styling according to Tuxedo Design System
 *
 * Color mapping:
 * - High yield (>10%): Emerald green
 * - Medium yield (5-10%): Amber
 * - Low yield (<5%): Neutral grey
 */
export const APYDisplay: React.FC<APYDisplayProps> = ({
  apy,
  showUnit = true,
  size = "medium",
}) => {
  // Determine semantic color class
  const getAPYClass = (value: number) => {
    if (value > 10) return "high";
    if (value >= 5) return "medium";
    return "low";
  };

  const apyClass = getAPYClass(apy);

  // Size mapping
  const sizeStyles = {
    small: {
      number: { fontSize: "16px" },
      unit: { fontSize: "10px" },
    },
    medium: {
      number: { fontSize: "24px" },
      unit: { fontSize: "12px" },
    },
    large: {
      number: { fontSize: "32px" },
      unit: { fontSize: "14px" },
    },
  };

  return (
    <div
      className="apy-display"
      style={{ display: "flex", alignItems: "baseline", gap: "4px" }}
    >
      <span
        className={`apy-value ${apyClass}`}
        style={{
          fontFamily: "var(--font-primary-serif)",
          fontWeight: "bold",
          ...sizeStyles[size].number,
        }}
      >
        {apy.toFixed(2)}
      </span>
      {showUnit && (
        <span
          className="apy-unit"
          style={{
            fontFamily: "var(--font-tertiary-mono)",
            fontWeight: "bold",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            ...sizeStyles[size].unit,
          }}
        >
          % APY
        </span>
      )}
    </div>
  );
};

export default APYDisplay;
