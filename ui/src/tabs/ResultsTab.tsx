import React, { useState } from 'react';
import { ColumnDef } from '@tanstack/react-table';
import { Award, Sparkles, TrendingUp, ShieldAlert, BarChart3, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';
import { CohortData, DiscoveryCurvesData, Scale100Row } from '../types';
import { InsightEngine } from '../insight/engine';
import { METRICS } from '../insight/metrics';
import { DataTable } from '../tables/DataTable';
import { DiscoveryCurvesChart } from '../charts/DiscoveryCurvesChart';

interface ResultsTabProps {
  data: CohortData | null;
  curves: DiscoveryCurvesData | null;
  cohort: 'pre_audit' | 'post_audit';
}

export const ResultsTab: React.FC<ResultsTabProps> = ({ data, curves, cohort }) => {
  const [showDisclosure, setShowDisclosure] = useState(false);

  if (!data) return <div className="p-8 text-center text-slate-500">Loading evaluation results...</div>;

  const rows: Scale100Row[] = data.scale100 || [];
  const headlineWins = InsightEngine.getHeadlineWins(data);
  const insights = InsightEngine.analyzeScale100(rows, cohort);

  // TanStack Table Column Definitions
  const columns: ColumnDef<Scale100Row, any>[] = [
    {
      accessorKey: 'method',
      header: 'Evaluated Method',
      cell: ({ row }) => {
        const name = row.original.method;
        const isTop1 = name.toLowerCase().includes('top-1') || name.toLowerCase().includes('treeranker');
        const isExpert = name.toLowerCase().includes('heuristic');
        const isChaosMonkey = name.toLowerCase().includes('chaos monkey') && !name.toLowerCase().includes('chaos monkey-2');

        return (
          <div className="flex items-center gap-2">
            <span className={`font-semibold ${isTop1 ? 'text-brand-300 font-bold' : isExpert ? 'text-amber-300' : 'text-slate-200'}`}>
              {name}
            </span>
            {isTop1 && (
              <span className="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 text-[10px] font-bold border border-brand-500/30 flex items-center gap-1">
                <Award size={11} /> Top-1
              </span>
            )}
            {isChaosMonkey && (
              <span className="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-mono">
                Baseline
              </span>
            )}
          </div>
        );
      }
    },
    {
      accessorKey: 'audc',
      header: 'Normalized AUDC (Sample Eff.)',
      cell: ({ row }) => {
        const val = row.original.audc;
        const ci = row.original.audc_ci;
        const isWinner = val >= 0.076 && val < 0.2; // Top-1 learned leader
        return (
          <div>
            <span className={`font-bold ${isWinner ? 'text-brand-400 font-mono text-sm' : 'text-slate-200'}`}>
              {METRICS.audc.format(val)}
            </span>
            {ci && <span className="block text-[10px] text-slate-500 font-mono">{ci}</span>}
          </div>
        );
      }
    },
    {
      accessorKey: 'recall',
      header: 'Weakness Recall',
      cell: ({ row }) => {
        const val = row.original.recall;
        const ci = row.original.recall_ci;
        return (
          <div>
            <span className="text-slate-200 font-mono font-medium">{METRICS.recall.format(val)}</span>
            {ci && <span className="block text-[10px] text-slate-500 font-mono">{ci}</span>}
          </div>
        );
      }
    },
    {
      accessorKey: 'damage',
      header: 'Collateral Damage (SLO)',
      cell: ({ row }) => {
        const val = row.original.damage;
        const ci = row.original.damage_ci;
        const isHigh = val > 10000;
        return (
          <div>
            <span className={`font-mono ${isHigh ? 'text-rose-400 font-bold' : 'text-slate-300'}`}>
              {METRICS.damage.format(val)}
            </span>
            {ci && <span className="block text-[10px] text-slate-500 font-mono">{ci}</span>}
          </div>
        );
      }
    },
    {
      accessorKey: 'simple_found',
      header: 'Simple Weaknesses',
      cell: ({ row }) => (
        <span className="text-slate-300 font-mono">{METRICS.simple_found.format(row.original.simple_found ?? 0)}</span>
      )
    },
    {
      accessorKey: 'compound_found',
      header: 'Compound Cascades',
      cell: ({ row }) => (
        <span className="text-slate-300 font-mono">{METRICS.compound_found.format(row.original.compound_found ?? 0)}</span>
      )
    }
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Headline Wins Banner */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Sparkles className="text-brand-400" size={18} />
            <span>Key Research Findings & Headline Wins</span>
          </h2>
          <span className="text-xs text-brand-400 font-mono font-semibold">
            {cohort === 'post_audit' ? 'Audited Run (n=30 systems, 3x Power)' : 'Original Run (n=10 systems)'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
          {headlineWins.map((win, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-slate-800 bg-slate-900/70 hover:border-brand-500/40 transition-all flex flex-col justify-between"
            >
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded border border-brand-500/20">
                  {win.badge}
                </span>
                <div className="text-xl font-extrabold text-white font-mono mt-1">{win.stat}</div>
                <div className="text-xs font-semibold text-slate-200">{win.title}</div>
              </div>
              <div className="text-[11px] text-slate-400 font-mono mt-2 pt-2 border-t border-slate-800/80">{win.sub}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Discovery Curves Explorer */}
      <div className="space-y-3">
        <DiscoveryCurvesChart curvesData={curves} cohort={cohort} />
      </div>

      {/* Main Benchmark Data Table with Insight Blocks */}
      <div className="space-y-3">
        <DataTable
          data={rows}
          columns={columns}
          insights={insights}
          title={`Scale-100 Microservice Main Comparison (${cohort === 'post_audit' ? 'Audited Run, Combined n=30' : 'Pre-Audit Run, n=10'})`}
          searchPlaceholder="Search method or baseline..."
        />
      </div>

      {/* Statistical Hypothesis Tests Section */}
      {data.statistical_tests && data.statistical_tests.length > 0 && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <TrendingUp className="text-brand-400" size={18} />
                <span>Rigorous Statistical Hypothesis Tests (Wilcoxon Signed-Rank with FDR Correction)</span>
              </h3>
              <p className="text-xs text-slate-400">
                Evaluating null hypothesis: Does ChaosRL Top-1 yield identical discovery efficiency to Netflix Chaos Monkey?
              </p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
              Target α = 0.05
            </span>
          </div>

          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="bg-slate-950 text-slate-300 border-b border-slate-800">
                  <th className="py-2.5 px-3">Comparison Hypothesis</th>
                  <th className="py-2.5 px-3">Mean AUDC Diff (Δ)</th>
                  <th className="py-2.5 px-3">Wilcoxon W</th>
                  <th className="py-2.5 px-3">Adjusted p-value</th>
                  <th className="py-2.5 px-3">Cohen's d</th>
                  <th className="py-2.5 px-3">Statistical Power</th>
                  <th className="py-2.5 px-3">Significance Verdict</th>
                </tr>
              </thead>
              <tbody>
                {data.statistical_tests.map((st: any, idx: number) => {
                  const isTopWin = (st.comparison || '').includes('ChaosRL Top-1 vs Chaos Monkey');
                  const pVal = st.p_adj ?? st.p_adjusted ?? st.p_value ?? 1.0;
                  const isSig = pVal < 0.05;

                  return (
                    <tr
                      key={idx}
                      className={`border-b border-slate-800/40 hover:bg-slate-800/40 font-mono ${
                        isTopWin ? 'bg-brand-950/20 text-brand-200' : 'text-slate-300'
                      }`}
                    >
                      <td className="py-2 px-3 font-sans font-semibold">{st.comparison}</td>
                      <td className="py-2 px-3">
                        {st.mean_diff > 0 ? `+${Number(st.mean_diff).toFixed(4)}` : Number(st.mean_diff).toFixed(4)}
                      </td>
                      <td className="py-2 px-3">{st.stat_w ?? st.w_stat ?? 'N/A'}</td>
                      <td className={`py-2 px-3 font-bold ${isSig ? 'text-brand-400' : 'text-slate-400'}`}>
                        {pVal < 0.001 ? '< 0.001' : Number(pVal).toFixed(4)}
                      </td>
                      <td className="py-2 px-3">{Number(st.cohen_d ?? 0).toFixed(3)}</td>
                      <td className="py-2 px-3">{`${(Number(st.power ?? 0) * 100).toFixed(1)}%`}</td>
                      <td className="py-2 px-3 font-sans">
                        {isSig ? (
                          <span className="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 text-[10px] font-bold border border-brand-500/30">
                            Statistically Significant (p &lt; 0.05)
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                            Not Significant
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Collapsible Disclosure Box */}
      <div className="rounded-xl border border-slate-800 bg-slate-950/60 overflow-hidden">
        <button
          onClick={() => setShowDisclosure(!showDisclosure)}
          className="w-full px-5 py-3 flex items-center justify-between text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          <span className="font-semibold">About these results, evaluation parameters & methodology disclosures</span>
          {showDisclosure ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>

        {showDisclosure && (
          <div className="px-5 pb-5 text-xs text-slate-400 space-y-2 border-t border-slate-800/60 pt-3 leading-relaxed">
            <p>
              • All experiments were evaluated across realistic directed acyclic graph (DAG) microservice topologies with N=100 service nodes under step budget B=100.
            </p>
            <p>
              • The <strong>Audited Run</strong> aggregates the original 10 systems with 20 fresh evaluation systems (seeds 42000-42019) generated by the independent verification engineer, bringing the cohort to n=30 independent systems and eliminating small-sample noise.
            </p>
            <p>
              • Normalized AUDC is defined as the definite integral of cumulative weaknesses triggered over the experiment budget divided by total budget B.
            </p>
            <p>
              • 95% Confidence Intervals are computed via non-parametric studentized bootstrap with 2,000 resamples.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

