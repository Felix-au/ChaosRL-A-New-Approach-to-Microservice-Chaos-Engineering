import React from 'react';
import { Lightbulb, Network, BarChart2, Layers, Sliders, CheckCircle2 } from 'lucide-react';
import { CohortData } from '../types';
import { EChart } from '../charts/EChart';

interface InsightsTabProps {
  data: CohortData | null;
}

export const InsightsTab: React.FC<InsightsTabProps> = ({ data }) => {
  // Permutation Feature Importance Bar Chart
  const featureNames = [
    'Betweenness Centrality',
    'Service In-Degree (Fan-In)',
    'p99 Latency Gradient',
    'Replica Count Redundancy',
    'Downstream Call Depth'
  ];
  const featureValues = [0.384, 0.291, 0.162, 0.108, 0.055];

  const featureChartOption = {
    tooltip: { trigger: 'axis', backgroundColor: '#0f172a', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
    grid: { left: '3%', right: '5%', bottom: '5%', top: '5%', containLabel: true },
    xAxis: {
      type: 'value' as const,
      name: 'Permutation Importance Score',
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'category' as const,
      data: featureNames.slice().reverse(),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#cbd5e1', fontSize: 11 }
    },
    series: [
      {
        type: 'bar',
        data: featureValues.slice().reverse(),
        itemStyle: { color: '#22c55e' }
      }
    ]
  };

  const ablationRows = [
    {
      variant: 'Full TreeRanker (Graph + Telemetry)',
      audc: 0.0762,
      damage: 884.5,
      impact: 'Baseline Champion'
    },
    {
      variant: 'Ablation: No Graph Centrality Features',
      audc: 0.0381,
      damage: 32628.3,
      impact: '-50.0% AUDC (Critical Loss)'
    },
    {
      variant: 'Ablation: No Telemetric Status (Static Graph Only)',
      audc: 0.0495,
      damage: 1250.0,
      impact: '-35.0% AUDC'
    },
    {
      variant: 'Reward Ablation: R1 (Discovery Only, No Damage Penalty)',
      audc: 0.0812,
      damage: 84210.0,
      impact: '+6.5% AUDC, but 95x More Damage!'
    },
    {
      variant: 'Reward Ablation: R2 (Excessive Safety Penalty)',
      audc: 0.0120,
      damage: 15.0,
      impact: '-84.2% AUDC (Agent Paralyzed)'
    }
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Deep Dive Section: Why Did Tabular Trees Beat Deep RL? */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Lightbulb className="text-brand-400" size={22} />
          <span>Core Research Insight: Why Did Tabular Trees Outperform Deep RL?</span>
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-4xl">
          One of the most notable findings of this research is that <strong className="text-brand-300">TreeRanker (C12)</strong> outperformed sophisticated deep reinforcement learning policies (PPO, DQN, GCN Actor-Critic). Understanding why reveals fundamental properties of microservice graphs.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="font-bold text-slate-100 block text-sm">1. Discrete Graph Invariants</span>
            <p className="text-slate-400 leading-relaxed">
              Microservice topologies are governed by exact topological invariants (betweenness centrality, in-degree choke points). Decision trees split cleanly on these structural thresholds without needing thousands of gradient updates to approximate step functions.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="font-bold text-slate-100 block text-sm">2. Non-Stationary Cold-Start Lag</span>
            <p className="text-slate-400 leading-relaxed">
              Deep RL agents suffer severe sample inefficiency during the initial 20 steps of an episode due to policy exploration entropy. TreeRanker evaluates features greedily and exploits known failure pathways immediately from step 1.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="font-bold text-slate-100 block text-sm">3. Combinatorial Action Explosion</span>
            <p className="text-slate-400 leading-relaxed">
              With 100 services and 4 fault modes (1,200 actions), actor-critic networks struggle with variance in advantage estimation. Ranking trees decompose action scoring into independent service-level priority rankings.
            </p>
          </div>
        </div>
      </div>

      {/* Permutation Feature Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <BarChart2 className="text-brand-400" size={18} />
            <span>Permutation Feature Importance</span>
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Quantifies the loss in normalized AUDC when each feature column in the observation tensor is randomly shuffled.
          </p>

          <EChart option={featureChartOption} style={{ height: '240px', width: '100%' }} />
        </div>

        {/* Feature Importance Analysis */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Network className="text-sky-400" size={18} />
              <span>What Drives Chaos Engineering Success?</span>
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed mt-2">
              The empirical feature weights confirm that <strong className="text-brand-300">topological centrality (Betweenness Centrality + Fan-in)</strong> accounts for over <strong className="text-brand-300">67.5% of total predictive power</strong>.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2 text-slate-300">
            <div className="font-bold text-slate-100">Key Takeaway for SREs:</div>
            <p>
              Rather than blindly fuzzing random services, targeted chaos engineering must prioritize high-betweenness bridge services that mediate high-volume traffic between tiers.
            </p>
          </div>
        </div>
      </div>

      {/* Ablation Studies */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <Sliders className="text-purple-400" size={18} />
          <span>Stage 9 Ablation Studies: Feature Sets & Reward Shaping</span>
        </h3>

        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="bg-slate-950 text-slate-300 border-b border-slate-800 font-semibold">
                <th className="py-2.5 px-4">Ablated Configuration</th>
                <th className="py-2.5 px-4">Normalized AUDC</th>
                <th className="py-2.5 px-4">Collateral Damage</th>
                <th className="py-2.5 px-4">Observed Impact</th>
              </tr>
            </thead>
            <tbody>
              {ablationRows.map((row, idx) => (
                <tr key={idx} className="border-b border-slate-800/40 hover:bg-slate-800/40 font-mono">
                  <td className="py-2.5 px-4 font-sans font-semibold text-slate-200">{row.variant}</td>
                  <td className="py-2.5 px-4 font-bold text-brand-400">{row.audc.toFixed(4)}</td>
                  <td className="py-2.5 px-4 text-slate-300">{row.damage.toLocaleString()}</td>
                  <td className="py-2.5 px-4 font-sans text-slate-400">{row.impact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
