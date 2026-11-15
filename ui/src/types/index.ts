export type DataSetCohort = 'pre_audit' | 'post_audit';

export type TabId =
  | 'overview'
  | 'approach'
  | 'methods'
  | 'results'
  | 'efficiency'
  | 'safety'
  | 'original_vs_audited'
  | 'insights'
  | 'rigor'
  | 'docs';

export interface MethodMetadata {
  id: string;
  tag: string;
  name: string;
  family: string;
  type: 'learned' | 'baseline' | 'ensemble' | 'oracle';
  is_top5: boolean;
  is_headline: boolean;
  rank: number;
  description: string;
  hyperparams: Record<string, any>;
  parameters: number;
  training_time_s: number;
  frozen_hash: string;
}

export interface ArchitectureStage {
  id: string;
  number: string;
  name: string;
  description: string;
  artifacts: string[];
  color: string;
}

export interface RigorData {
  unit_tests_passing: number;
  test_suite_coverage_pct: number;
  test_access_log_entries: number;
  test_access_violations: number;
  cryptographic_manifest_sha256: string;
  frozen_models_count: number;
  pre_registered_claims: number;
  claims_verified: number;
  claims_refuted: number;
  evaluation_cohort_pre_audit: number;
  evaluation_cohort_post_audit: number;
  statistical_power_pct: number;
  wilcoxon_adjusted_p_value: number;
  git_commit_sha: string;
  reproduction_commands: Array<{ label: string; command: string }>;
}

export interface CurvePoint {
  steps: number[];
  mean: number[];
  ci_low: number[];
  ci_high: number[];
  n_systems?: number;
}

export interface DiscoveryCurvesData {
  pre_audit: Record<string, CurvePoint>;
  post_audit: Record<string, CurvePoint>;
}

export interface GlossaryItem {
  name: string;
  definition: string;
  direction?: 'higher' | 'lower';
  unit?: string;
}

export interface SearchDocEntry {
  id: string;
  title: string;
  doc_title: string;
  category: string;
  rel_path: string;
  section: string;
  snippet: string;
  content: string;
}

export interface Scale100Row {
  method: string;
  tag?: string;
  audc: number;
  audc_ci: string;
  recall: number;
  recall_ci: string;
  damage: number;
  damage_ci: string;
  simple_found?: number;
  compound_found?: number;
  n?: number;
}

export interface CohortData {
  cohort_name: string;
  cohort_description: string;
  n_systems: number;
  scale100: Scale100Row[];
  multiscale: any[];
  budget_sweep: any[];
  statistical_tests: any[];
  statistical_slices?: Record<string, any[]>;
  family_m: any[];
  ablation: any[];
}

