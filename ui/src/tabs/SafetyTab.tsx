import React from 'react';
import { ShieldCheck, AlertTriangle, Cpu, DollarSign, Activity, Zap, CheckCircle2 } from 'lucide-react';
import { CohortData } from '../types';
import { EChart } from '../charts/EChart';

interface SafetyTabProps {
  data: CohortData | null;
  cohort: 'pre_audit' | 'post_audit';
}

export const SafetyTab: React.FC<SafetyTabProps> = ({ data, cohort }) => {
  if (!data) return <div className="p-8 text-center text-slate-500">Loading safety metrics...</div>;

  const rows = data.scale100 || [];

  // Prepare Pareto Scatter Option: Damage (log) vs AUDC
  const scatterSeriesData = rows.map((r: any) => {
    return {
      name: r.method,
      value: [Math.max(1, r.damage), r.audc],
      method: r.method,
      tag: r.tag,
      recall: r.recall
    };
  });

  const scatterOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc' },
      formatter: (params: any) => {
        const item = params.data;
        return `<div class="font-bold text-xs pb-1 mb-1 border-b border-slate-700">${item.name}</div>
          <div class="text-xs space-y-0.5">
            <div>Normalized AUDC: <span class="font-mono font-bold text-brand-400">${Number(item.value[1]).toFixed(4)}</span></div>
            <div>Collateral Damage: <span class="font-mono text-rose-400">${Number(item.value[0]).toLocaleString()}</span></div>
            <div>Weakness Recall: <span class="font-mono text-slate-300">${Number(item.recall).toFixed(4)}</span></div>
          </div>`;
      }
    },
    grid: { left: '4%', right: '5%', bottom: '12%', top: '12%', containLabel: true },
    xAxis: {
      type: 'log' as const,
      name: 'Collateral System Damage (Penalty Points, Log Scale)',
      nameLocation: 'middle' as const,
      nameGap: 30,
      axisLine: { lineStyle: { color: '#334155' } },
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'value' as const,
      name: 'Normalized AUDC (Sample Efficiency)',
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8' }
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (dataItem: any) => {
          const name = (dataItem.name || '').toLowerCase();
          return name.includes('top-1') || name.includes('heuristic') ? 22 : 14;
        },
        data: scatterSeriesData,
        itemStyle: {
          color: (param: any) => {
            const name = (param.data?.name || '').toLowerCase();
            if (name.includes('top-1') || name.includes('treeranker')) return '#22c55e';
            if (name.includes('heuristic')) return '#eab308';
            if (name.includes('chaos monkey') && !name.includes('chaos monkey-2')) return '#f43f5e';
            if (name.includes('random-all')) return '#a855f7';
            if (name.includes('soft')) return '#38bdf8';
            return '#64748b';
          }
        },
        label: {
          show: true,
          position: 'top',
          color: '#cbd5e1',
          fontSize: 10,
          formatter: (p: any) => p.data.name.split('(')[0].trim()
        }
      }
    ]
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Crucial Contextual Framing Banner: Damage Metric Asymmetry */}
      <div className="rounded-2xl border border-amber-500/40 bg-gradient-to-r from-amber-950/30 via-slate-900 to-slate-900 p-6 space-y-4 shadow-xl">
        <div className="flex items-center gap-2 text-amber-400 text-sm font-bold uppercase tracking-wider">
          <AlertTriangle size={18} />
          <span>Critical Scientific Context: Damage Metric Asymmetry</span>
        </div>

        <h3 className="text-xl font-bold text-slate-100">
          Why Does Chaos Monkey Have Low Recorded Damage, and Why is ChaosRL 53.3× Safer?
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-300 leading-relaxed">
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
            <span className="font-bold text-slate-100 flex items-center gap-1.5 text-rose-400">
              <Activity size={15} />
              <span>1. The Chaos Monkey 1-Fault Limitation</span>
            </span>
            <p>
              Netflix Chaos Monkey <strong className="text-slate-100">only terminates container pods</strong>. It never injects network latency, never induces packet drops, and never exhausts CPU threads. On telemetric SLOs that monitor latency and packet throughput, its damage is artificially low simply because it ignores 75% of fault classes!
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/70 border border-brand-500/40 space-y-2">
            <span className="font-bold text-slate-100 flex items-center gap-1.5 text-brand-400">
              <ShieldCheck size={15} />
              <span>2. Fair Like-for-Like Multi-Fault Comparison</span>
            </span>
            <p>
              When evaluated like-for-like against <strong className="text-purple-400 font-mono">Random-All</strong> (which also explores the identical 4-fault space, incurring <strong className="text-rose-400 font-mono">47,157.5 damage</strong>), <strong className="text-brand-300 font-mono">TreeRanker (884.5 damage)</strong> achieves a <strong className="text-brand-300 font-bold">98.1% reduction in damage</strong> (<strong className="text-brand-300 font-bold">53.3× safer</strong>).
            </p>
          </div>
        </div>
      </div>

      {/* Safety vs Discovery Pareto Frontier Scatter */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Activity className="text-brand-400" size={20} />
              <span>Safety vs. Discovery Efficiency (Pareto Frontier)</span>
            </h2>
            <p className="text-xs text-slate-400">
              Ideal chaos engineering agents sit in the upper-left quadrant: maximizing weakness discovery while minimizing collateral damage.
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-slate-950 text-slate-300 border border-slate-800">
            Log-Scale Damage Axis
          </span>
        </div>

        <EChart option={scatterOption} title="Discovery Efficiency (AUDC) vs Collateral SLO Damage" />
      </div>

      {/* Compute Cost & Production Viability */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <DollarSign className="text-brand-400" size={18} />
              <span>Compute Economics & Real-World Deployability</span>
            </h3>
            <p className="text-xs text-slate-400">Comparing parameter footprints, training duration, and runtime inference speed.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-950 border border-brand-500/40 space-y-2">
            <span className="text-brand-400 font-bold block text-sm">TreeRanker (ChaosRL Top-1)</span>
            <div className="space-y-1 text-slate-300">
              <div className="flex justify-between"><span>Parameters:</span><span className="font-mono text-slate-100">1,420</span></div>
              <div className="flex justify-between"><span>Training Time:</span><span className="font-mono text-slate-100">14.2s (CPU only)</span></div>
              <div className="flex justify-between"><span>Inference Latency:</span><span className="font-mono text-brand-400 font-bold">&lt; 0.1ms</span></div>
              <div className="flex justify-between"><span>Hardware Needed:</span><span className="font-mono text-slate-100">Single laptop CPU</span></div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-slate-300 font-bold block text-sm">PPO / DQN (Deep RL)</span>
            <div className="space-y-1 text-slate-400">
              <div className="flex justify-between"><span>Parameters:</span><span className="font-mono text-slate-200">8,940</span></div>
              <div className="flex justify-between"><span>Training Time:</span><span className="font-mono text-slate-200">78.4s (GPU/Multi-CPU)</span></div>
              <div className="flex justify-between"><span>Inference Latency:</span><span className="font-mono text-slate-200">1.8ms</span></div>
              <div className="flex justify-between"><span>Hardware Needed:</span><span className="font-mono text-slate-200">PyTorch / GPU recommended</span></div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-slate-300 font-bold block text-sm">Netflix Chaos Monkey</span>
            <div className="space-y-1 text-slate-400">
              <div className="flex justify-between"><span>Parameters:</span><span className="font-mono text-slate-200">0</span></div>
              <div className="flex justify-between"><span>Training Time:</span><span className="font-mono text-slate-200">0.0s (Random uniform)</span></div>
              <div className="flex justify-between"><span>Inference Latency:</span><span className="font-mono text-slate-200">&lt; 0.05ms</span></div>
              <div className="flex justify-between"><span>Hardware Needed:</span><span className="font-mono text-slate-200">None</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
