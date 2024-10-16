export interface Distinct {
  count: number;
  percent: number;
}

export interface Quantiles {
  q25: number;
  q50: number;
  q75: number;
  q99: number;
}

export interface Histogram {
  bins: number[];
  bin_counts: number[];
}

export interface CharStats {
  min_length: number;
  max_length: number;
  median_length: number;
  mean_length: number;
}

export interface WordStats {
  words: Record<string, Distinct>;
}

export interface StringStats {
  distinct: Distinct;
  char_stats: CharStats;
  word_stats: WordStats;
}

export interface NumericStats {
  mean: number;
  stddev: number;
  min: number;
  max: number;
  distinct: Distinct;
  quantiles: Quantiles;
  histogram: Histogram;
}

export interface FeatureProfile {
  id: string;
  numeric_stats: NumericStats | undefined;
  string_stats: StringStats | undefined;
  timestamp: string;
}

export interface DataProfile {
  features: Record<string, FeatureProfile>;
}
