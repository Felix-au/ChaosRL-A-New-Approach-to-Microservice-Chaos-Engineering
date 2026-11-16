export interface MetricDefinition {
  key: string;
  name: string;
  shortName: string;
  direction: 'higher' | 'lower';
  unit: string;
  decimals: number;
  description: string;
  glossaryKey?: string;
  format: (value: number) => string;
}

export const METRICS: Record<string, MetricDefinition> = {
  audc: {
    key: 'audc',
    name: 'Normalized AUDC (Area Under Discovery Curve)',
    shortName: 'AUDC',
    direction: 'higher',
    unit: 'ratio [0-1]',
    decimals: 4,
    description: 'Integral of cumulative weakness discovery over time. Rewards early discovery.',
    glossaryKey: 'AUDC',
    format: (v: number) => (v != null ? Number(v).toFixed(4) : 'N/A')
  },
  recall: {
    key: 'recall',
    name: 'Weakness Recall',
    shortName: 'Recall',
    direction: 'higher',
    unit: 'ratio [0-1]',
    decimals: 4,
    description: 'Fraction of total seeded system vulnerabilities uncovered within the budget.',
    glossaryKey: 'Weakness Recall',
    format: (v: number) => (v != null ? Number(v).toFixed(4) : 'N/A')
  },
  damage: {
    key: 'damage',
    name: 'Collateral System Damage',
    shortName: 'Damage',
    direction: 'lower',
    unit: 'penalty points',
    decimals: 1,
    description: 'Cumulative SLO degradation (latency spikes, HTTP 500s) during testing.',
    glossaryKey: 'Collateral Damage',
    format: (v: number) => {
      if (v == null) return 'N/A';
      if (v >= 1000000) return `${(v / 1000000).toFixed(1)}M`;
      if (v >= 1000) return `${(v / 1000).toFixed(1)}k`;
      return Number(v).toFixed(1);
    }
  },
  simple_found: {
    key: 'simple_found',
    name: 'Mean Simple Weaknesses Found',
    shortName: 'Simple Found',
    direction: 'higher',
    unit: 'count',
    decimals: 2,
    description: 'Average number of single-point-of-failure bottlenecks triggered per system.',
    format: (v: number) => (v != null ? Number(v).toFixed(2) : 'N/A')
  },
  compound_found: {
    key: 'compound_found',
    name: 'Mean Compound Cascades Found',
    shortName: 'Compound Found',
    direction: 'higher',
    unit: 'count',
    decimals: 2,
    description: 'Average number of multi-service cascading failures triggered per system.',
    format: (v: number) => (v != null ? Number(v).toFixed(2) : 'N/A')
  },
  power: {
    key: 'power',
    name: 'Statistical Power',
    shortName: 'Power',
    direction: 'higher',
    unit: '%',
    decimals: 1,
    description: 'Probability of detecting a true effect of the observed magnitude.',
    format: (v: number) => (v != null ? `${(Number(v) * 100).toFixed(1)}%` : 'N/A')
  },
  p_value: {
    key: 'p_value',
    name: 'Adjusted p-value (Wilcoxon)',
    shortName: 'p-value',
    direction: 'lower',
    unit: 'p',
    decimals: 4,
    description: 'Benjamini-Hochberg FDR corrected significance level.',
    format: (v: number) => {
      if (v == null) return 'N/A';
      return v < 0.001 ? '< 0.001' : Number(v).toFixed(4);
    }
  }
};

