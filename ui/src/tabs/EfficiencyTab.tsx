import React from 'react';
import { Clock, Network, Layers, TrendingUp, Zap, Sparkles } from 'lucide-react';
import { CohortData } from '../types';
import { EChart } from '../charts/EChart';

interface EfficiencyTabProps {
  data: CohortData | null;
  cohort: 'pre_audit' | 'post_audit';
}

export const EfficiencyTab: React.FC<EfficiencyTabProps> = ({ data, cohort }) => {
  if (!data) return <div className="p-8 text-center text-slate-500">Loading efficiency metrics...</div>;

  const budgetData = data.budget_sweep || [];
  const multiScaleData = data.multiscale || [];
  const familyMData = data.family_m || [];

  // Budget Sweep Chart Option
  const budgetCategories = budgetData.map((b: any) => `B=${b.budget ?? b.Budget}`);
  const budgetSeries = [
    {
      name: 'ChaosRL Top-1 (TreeRanker)',
      type: 'line',
      data: budgetData.map((b: any) => Number(b.top1 ?? b.C12 ?? b['ChaosRL Top-1'] ?? 0)),
      itemStyle: { color: '#22c55e' },
      lineStyle: { width: 3 }
    },
    {
      name: 'Heuristic Expert',
      type: 'line',
      data: budgetData.map((b: any) => Number(b.heuristic ?? b['Heuristic Expert'] ?? 0)),
      itemStyle: { color: '#eab308' },
      lineStyle: { width: 2, type: 'dashed' }
    },
    {
      name: 'Chaos Monkey (Faithful)',
      type: 'line',
      data: budgetData.map((b: any) => Number(b.chaos_monkey ?? b['Chaos Monkey'] ?? 0)),
      itemStyle: { color: '#f43f5e' },
      lineStyle: { width: 2 }
    }
  ];

  const budgetOption = {
    tooltip: { trigger: 'axis', backgroundColor: '#0f172a', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
    legend: { textStyle: { color: '#94a3b8' }, top: '2%' },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category' as const,
      data: budgetCategories,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'value' as const,
      name: 'Normalized AUDC',
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8' }
    },
    series: budgetSeries
  };

  // MultiScale Bar Chart Option
  const scaleCategories = multiScaleData.map((m: any) => `N=${m.scale ?? m.Scale} Services`);
  const scaleSeries = [
    {
      name: 'ChaosRL Top-1 (TreeRanker)',
      type: 'bar',
      data: multiScaleData.map((m: any) => Number(m.top1 ?? m.C12 ?? m['ChaosRL Top-1'] ?? 0)),
      itemStyle: { color: '#22c55e' }
    },
    {
      name: 'Heuristic Expert',
      type: 'bar',
      data: multiScaleData.map((m: any) => Number(m.heuristic ?? m['Heuristic Expert'] ?? 0)),
      itemStyle: { color: '#eab308' }
    },
    {
      name: 'Chaos Monkey',
      type: 'bar',
      data: multiScaleData.map((m: any) => Number(m.chaos_monkey ?? m['Chaos Monkey'] ?? 0)),
      itemStyle: { color: '#f43f5e' }
    }
  ];

  const scaleOption = {
    tooltip: { trigger: 'axis', backgroundColor: '#0f172a', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
    legend: { textStyle: { color: '#94a3b8' }, top: '2%' },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category' as const,
      data: scaleCategories,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'value' as const,
      name: 'Normalized AUDC',
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8' }
    },
    series: scaleSeries
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Low-Budget Sample Efficiency Section */}
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Clock className="text-brand-400" size={20} />
                <span>Low-Budget Sample Efficiency (B=25 to B=200 Steps)</span>
              </h2>
              <p className="text-xs text-slate-400">
                In time-constrained CI/CD pipelines, engineers can only afford short chaos tests.
              </p>
            </div>
            <span className="text-xs font-mono px-3 py-1 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 font-bold">
              7.0× Win at B=25 Steps
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <EChart
                option={budgetOption}
                title="Discovery Efficiency vs Experiment Budget"
                tableData={budgetData}
                tableColumns={[
                  { key: 'budget', label: 'Budget' },
                  { key: 'top1', label: 'Top-1 AUDC' },
                  { key: 'chaos_monkey', label: 'Chaos Monkey' },
                  { key: 'heuristic', label: 'Heuristic' }
                ]}
              />
            </div>

            <div className="space-y-3 flex flex-col justify-center">
              <div className="p-4 rounded-xl bg-brand-950/20 border border-brand-500/40 text-xs text-brand-200 space-y-2">
                <div className="flex items-center gap-2 font-bold text-brand-300">
                  <Zap size={16} />
                  <span>Immediate CI/CD Feedback</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  At the tightest budget of <strong className="text-brand-300 font-mono">B=25 steps</strong>, TreeRanker discovers vulnerabilities with an AUDC of <strong className="text-brand-300 font-mono">0.0547</strong> versus <strong className="text-rose-400 font-mono">0.0078</strong> for Chaos Monkey (<strong className="text-brand-300 font-bold">7.0× higher sample efficiency</strong>).
                </p>
                <p className="text-slate-400 text-[11px]">
                  Random baselines fail to encounter critical weakness combinations before the budget expires, while learned agents hone directly into structural bottlenecks.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1">
                <span className="font-semibold text-slate-300 block">Practical Production Takeaway:</span>
                <span>Enables 3-minute pull-request verification runs instead of overnight 8-hour chaos drills.</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Scale Scalability Section */}
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Network className="text-sky-400" size={20} />
                <span>Multi-Scale System Scalability (N=20 to N=500 Services)</span>
              </h2>
              <p className="text-xs text-slate-400">
                Evaluating policy robustness as microservice topologies scale from small pods to hyper-scale meshes.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <EChart
                option={scaleOption}
                title="AUDC Performance Across Service Network Sizes"
                tableData={multiScaleData}
                tableColumns={[
                  { key: 'scale', label: 'Scale N' },
                  { key: 'top1', label: 'Top-1 AUDC' },
                  { key: 'chaos_monkey', label: 'Chaos Monkey' },
                  { key: 'heuristic', label: 'Heuristic' }
                ]}
              />
            </div>

            <div className="space-y-3 flex flex-col justify-center">
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2">
                <span className="font-bold text-slate-200 block">1. Small-to-Medium Superiority (N=20)</span>
                <p className="text-slate-400 leading-relaxed">
                  On medium topologies (<strong className="text-slate-200 font-mono">N=20 services</strong>), TreeRanker achieves <strong className="text-brand-300 font-mono">0.2369 AUDC</strong>, clearly outperforming Chaos Monkey (<strong className="text-slate-400 font-mono">0.2097</strong>).
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2">
                <span className="font-bold text-slate-200 block">2. Hyper-Scale Robustness (N=500)</span>
                <p className="text-slate-400 leading-relaxed">
                  In massive graphs with 500 services, random exploration collapses due to the immense action space. TreeRanker maintains a <strong className="text-brand-300 font-mono">4.08× advantage</strong> over Chaos Monkey (<strong className="text-brand-300 font-mono">0.0162 vs 0.00397</strong>).
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Out-of-Distribution Generalization: Family M */}
      {familyMData.length > 0 && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Layers className="text-purple-400" size={18} />
                <span>Zero-Shot Topology Generalization: Family M (Service Mesh)</span>
              </h2>
              <p className="text-xs text-slate-400">
                Evaluating frozen models zero-shot on cyclic mesh topologies without retraining.
              </p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
              Mesh Topology Transfer
            </span>
          </div>

          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="bg-slate-950 text-slate-300 border-b border-slate-800 font-semibold">
                  <th className="py-2.5 px-4">Method</th>
                  <th className="py-2.5 px-4">Normalized AUDC</th>
                  <th className="py-2.5 px-4">Weakness Recall</th>
                  <th className="py-2.5 px-4">Collateral Damage</th>
                  <th className="py-2.5 px-4">Simple Found</th>
                  <th className="py-2.5 px-4">Compound Found</th>
                </tr>
              </thead>
              <tbody>
                {familyMData.map((row: any, idx: number) => (
                  <tr key={idx} className="border-b border-slate-800/40 hover:bg-slate-800/40 font-mono">
                    <td className="py-2.5 px-4 font-sans font-semibold text-slate-200">{row.method ?? row.Method}</td>
                    <td className="py-2.5 px-4 font-bold text-brand-400">{Number(row.audc ?? row['Normalized AUDC'] ?? 0).toFixed(4)}</td>
                    <td className="py-2.5 px-4 text-slate-300">{Number(row.recall ?? row['Weakness Recall'] ?? 0).toFixed(4)}</td>
                    <td className="py-2.5 px-4 text-slate-300">{Number(row.damage ?? row['Cumulative Damage'] ?? 0).toFixed(1)}</td>
                    <td className="py-2.5 px-4 text-slate-400">{Number(row.simple_found ?? row['Mean Simple Found'] ?? 0).toFixed(2)}</td>
                    <td className="py-2.5 px-4 text-slate-400">{Number(row.compound_found ?? row['Mean Compound Found'] ?? 0).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
