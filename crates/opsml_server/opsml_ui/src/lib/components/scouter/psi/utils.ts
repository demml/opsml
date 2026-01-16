import type { PsiThreshold } from "./types";

export function getPsiThresholdKeyValue(threshold: PsiThreshold): {
  type: string;
  value: number;
} {
  if (threshold.Normal) {
    return { type: "Normal", value: threshold.Normal.alpha };
  } else if (threshold.ChiSquare) {
    return { type: "ChiSquare", value: threshold.ChiSquare.alpha };
  } else if (threshold.Fixed) {
    return { type: "Fixed", value: threshold.Fixed.threshold };
  }
  throw new Error("Invalid PsiThreshold configuration");
}

export function updatePsiThreshold(type: string, value: number): PsiThreshold {
  const numericValue = Number(value);

  if (isNaN(numericValue)) {
    throw new Error(`Invalid numeric value: ${value}`);
  }

  switch (type) {
    case "Normal":
      return { Normal: { alpha: numericValue } };
    case "ChiSquare":
      return { ChiSquare: { alpha: numericValue } };
    case "Fixed":
      return { Fixed: { threshold: numericValue } };
    default:
      throw new Error(`Unknown threshold type: ${type}`);
  }
}
