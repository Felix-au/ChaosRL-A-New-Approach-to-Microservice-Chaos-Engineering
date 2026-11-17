import React, { useState } from 'react';
import { EChart } from './EChart';
import { DiscoveryCurvesData } from '../types';

interface DiscoveryCurvesChartProps {
  curvesData: DiscoveryCurvesData | null;
  cohort: 'pre_audit' | 'post_audit';
}

const METHOD_COLORS: Record<string, string> = {
  C12: '#22c55e',          // TreeRanker - Vibrant Green
  e1_soft: '#38bdf8',      // Soft Vote - Light Blue
  heuristic: '#eab308',    // Heuristic Expert - Amber
  chaos_monkey: '#f43f5e', // Chaos Monkey - Rose
  chaos_monkey_2: '#fb7185',
  random_all: '#a855f7',   // Random-All - Purple
  round_robin: '#64748b',  // Slate
  bandit_ucb: '#f97316',   // Orange
  oracle: '#10b981'        // Emerald
};

const METHOD_LABELS: Record<string, string> = {
  C12: 'ChaosRL Top-1 (TreeRanker)',
  e1_soft: 'ChaosRL Ensemble (Soft Vote)',
  heuristic: 'Heuristic Expert',
  chaos_monkey: 'Chaos Monkey (Faithful)',
  chaos_monkey_2: 'Chaos Monkey-2',
  random_all: 'Random-All',
  round_robin: 'Round-Robin',
  bandit_ucb: 'Bandit UCB',
  oracle: 'Oracle Upper Bound'
};

export const DiscoveryCurvesChart: React.FC<DiscoveryCurvesChartProps> = ({ curvesData, cohort }) => {
  const [selectedMethods, setSelectedMethods] = useState<string[]>([
    'C12',
    'heuristic',
    'chaos_monkey',
    'random_all',
    'e1_soft'
  ]);

  if (!curvesData) return <div className="p-8 text-center text-slate-500">Loading curve data...</div>;

  const dataset = cohort === 'post_audit' ? curvesData.post_audit : curvesData.pre_audit;
  const availableMethods = Object.keys(dataset);

  const toggleMethod = (m: string) => {
    setSelectedMethods((prev) =>
      prev.includes(m) ? prev.filter((item) => item !== m) : [...prev, m]
    );
  };

  // Build ECharts series
  const series: any[] = [];
  let steps: number[] = [];

  selectedMethods.forEach((methodKey) => {
    const data = dataset[methodKey];
    if (!data) return;

    steps = data.steps;
    const color = METHOD_COLORS[methodKey] || '#94a3b8';
    const label = METHOD_LABELS[methodKey] || methodKey;

    // Mean Line
    series.push({
      name: label,
      type: 'line',
      data: data.mean,
      smooth: true,
      showSymbol: false,
      lineStyle: {
        width: methodKey === 'C12' || methodKey === 'chaos_monkey' ? 3 : 2,
        color
      },
      itemStyle: { color },
      z: methodKey === 'C12' ? 5 : 2
    });

    // 95% Confidence Interval Area (Upper & Lower)
    series.push({
      name: `${label} (95% CI)`,
      type: 'line',
      data: data.ci_high,
      lineStyle: { opacity: 0 },
      stack: `ci-${methodKey}`,
      symbol: 'none'
    });

    series.push({
      name: `${label} (95% CI)`,
      type: 'line',
      data: data.ci_high.map((h, i) => Math.max(0, h - data.ci_low[i])),
      lineStyle: { opacity: 0 },
      areaStyle: {
        color,
        opacity: 0.12
      },
      stack: `ci-${methodKey}`,
      symbol: 'none'
    });
  });

  const chartOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc', fontSize: 12 },
      formatter: (params: any[]) => {
        let text = `<div class="font-bold text-xs pb-1 mb-1 border-b border-slate-700">Step ${params[0]?.name || ''}</div>`;
        params.forEach((p) => {
          if (!p.seriesName.includes('95% CI')) {
            text += `<div class="flex items-center justify-between gap-4 py-0.5 text-xs">
              <span style="color:${p.color}">● ${p.seriesName}</span>
              <span class="font-mono font-bold">${Number(p.value).toFixed(4)}</span>
            </div>`;
          }
        });
        return text;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category' as const,
      data: steps,
      name: 'Experiment Step (Budget T=100)',
      nameLocation: 'middle' as const,
      nameGap: 28,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 }
    },
    yAxis: {
      type: 'value' as const,
      name: 'Cumulative Vulnerabilities Found (Recall)',
      axisLine: { lineStyle: { color: '#334155' } },
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 }
    },
    series
  };

  return (
    <div className="space-y-3">
      {/* Method filter chips */}
      <div className="flex flex-wrap items-center gap-1.5 p-2 bg-slate-950/60 rounded-lg border border-slate-800">
        <span className="text-xs font-semibold text-slate-400 mr-2">Visible Policies:</span>
        {availableMethods.map((m) => {
          const isSelected = selectedMethods.includes(m);
          const color = METHOD_COLORS[m] || '#94a3b8';
          return (
            <button
              key={m}
              onClick={() => toggleMethod(m)}
              className={`px-2.5 py-1 rounded-full text-xs font-medium transition-all flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-slate-800 text-slate-100 border border-slate-700 shadow-sm'
                  : 'bg-slate-900/40 text-slate-500 border border-transparent hover:text-slate-300'
              }`}
            >
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
              <span>{METHOD_LABELS[m] || m}</span>
            </button>
          );
        })}
      </div>

      <EChart
        option={chartOption}
        title={`Continuous Weakness Discovery Trajectory (${cohort === 'post_audit' ? 'Audited Run, n=30' : 'Pre-Audit Run, n=10'})`}
      />
    </div>
  );
};
