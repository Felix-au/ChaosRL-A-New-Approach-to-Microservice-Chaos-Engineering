import React, { useState } from 'react';
import confetti from 'canvas-confetti';
import { Sparkles, ArrowRight, ArrowLeft, X, CheckCircle2 } from 'lucide-react';
import { TabId } from '../types';

interface GuidedTourProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateTab: (tabId: TabId) => void;
}

interface TourStep {
  tab: TabId;
  title: string;
  description: string;
  highlight: string;
}

const TOUR_STEPS: TourStep[] = [
  {
    tab: 'overview',
    title: '1. The ChaosRL Problem & Mission',
    description: 'Netflix Chaos Monkey terminates random instances with no memory and only 1 fault mode. ChaosRL replaces random selection with learned, multi-fault policies that expose critical weaknesses with fewer experiments.',
    highlight: 'Explore the interactive failure-cascade simulator and system overview.'
  },
  {
    tab: 'approach',
    title: '2. High-Throughput Calibrated Simulation',
    description: 'Our Gym environment runs at ~12,000 steps/sec, calibrated directly on empirical trace data from real microservices (Sock-Shop & Train-Ticket).',
    highlight: 'Review the log-normal latency distributions and failure propagation mechanics.'
  },
  {
    tab: 'methods',
    title: '3. Diverse Candidate Pool & Top-5 Freeze',
    description: 'We evaluated 12 algorithms across 5 paradigms: Tabular Trees, Deep RL (PPO, DQN, GCN), Contextual Bandits, and Ensembles. The top 5 models were cryptographically SHA-256 frozen before final evaluation.',
    highlight: 'Filter through candidate models and inspect frozen hashes.'
  },
  {
    tab: 'results',
    title: '4. Headline Results & Statistical Victory',
    description: 'TreeRanker (ChaosRL Top-1) beats Chaos Monkey with a 2.38× higher Normalized AUDC (0.0762 vs 0.0320), confirmed at p = 0.0037 with 96.1% statistical power across n=30 microservice systems.',
    highlight: 'Inspect the discovery trajectory curves and confidence bands.'
  },
  {
    tab: 'efficiency',
    title: '5. Sample Efficiency & Low-Budget Speed',
    description: 'In constrained testing budgets (B=25 steps), TreeRanker uncovers vulnerabilities 7.0× faster than random exploration (AUDC 0.0547 vs 0.0078), providing rapid feedback for CI/CD pipelines.',
    highlight: 'Check the budget sweep and scale-up comparisons up to N=500 services.'
  },
  {
    tab: 'safety',
    title: '6. Damage Metric Asymmetry Context',
    description: 'Chaos Monkey only terminates pods, giving it artificially low recorded damage. When evaluated against Random-All over the same 4-fault space, TreeRanker is 53.3× safer with a 98.1% reduction in SLO degradation.',
    highlight: 'Inspect the Pareto safety frontier scatter chart.'
  },
  {
    tab: 'original_vs_audited',
    title: '7. Independent Audit & Tripled Power',
    description: 'An independent audit re-evaluated the entire framework, expanding the test cohort from n=10 to n=30 systems. This confirmed TreeRanker\'s advantage from an underpowered trend (p=0.121) to statistical significance (p=0.0037).',
    highlight: 'Compare pre-audit vs post-audit results side-by-side.'
  },
  {
    tab: 'insights',
    title: '8. Tabular Tree vs. Deep RL Discovery',
    description: 'Why did TreeRanker beat Deep RL? In discrete microservice graphs, structural graph metrics (centrality, in-degree) provide explicit, non-stationary topological priors that tabular trees exploit faster than neural approximations.',
    highlight: 'Review permutation feature importance and ablation tests.'
  },
  {
    tab: 'rigor',
    title: '9. Cryptographic Rigor & Zero Data Leakage',
    description: '104 passing tests, 1,240 audited test accesses with 0 leakage violations, SHA-256 frozen checkpoints, and 72 verified claims.',
    highlight: 'Verify the test access logs and reproduction commands.'
  }
];

export const GuidedTour: React.FC<GuidedTourProps> = ({ isOpen, onClose, onNavigateTab }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  if (!isOpen) return null;

  const currentStep = TOUR_STEPS[currentStepIndex];
  const isLast = currentStepIndex === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (isLast) {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });
      onClose();
    } else {
      const nextIdx = currentStepIndex + 1;
      setCurrentStepIndex(nextIdx);
      onNavigateTab(TOUR_STEPS[nextIdx].tab);
    }
  };

  const handlePrev = () => {
    if (currentStepIndex > 0) {
      const prevIdx = currentStepIndex - 1;
      setCurrentStepIndex(prevIdx);
      onNavigateTab(TOUR_STEPS[prevIdx].tab);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg rounded-2xl border border-brand-500/40 bg-slate-900 shadow-2xl p-6 relative overflow-hidden">
        {/* Glow backdrop */}
        <div className="absolute top-0 right-0 w-48 h-48 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Header */}
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
          <div className="flex items-center gap-2 text-brand-400 text-xs font-bold uppercase tracking-wider">
            <Sparkles size={16} />
            <span>Interactive Guided Tour</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X size={16} />
          </button>
        </div>

        {/* Step Content */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-base font-bold text-slate-100">{currentStep.title}</h4>
            <span className="text-xs font-mono text-slate-400">
              {currentStepIndex + 1} / {TOUR_STEPS.length}
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{currentStep.description}</p>
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 text-xs text-brand-300 flex items-start gap-2">
            <CheckCircle2 size={15} className="text-brand-400 mt-0.5 shrink-0" />
            <span>{currentStep.highlight}</span>
          </div>
        </div>

        {/* Navigation & Progress */}
        <div className="flex items-center justify-between pt-5 mt-4 border-t border-slate-800">
          <button
            onClick={handlePrev}
            disabled={currentStepIndex === 0}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              currentStepIndex === 0
                ? 'text-slate-600 cursor-not-allowed'
                : 'text-slate-300 bg-slate-800 hover:bg-slate-700'
            }`}
          >
            <ArrowLeft size={14} />
            <span>Previous</span>
          </button>

          <div className="flex gap-1">
            {TOUR_STEPS.map((_, i) => (
              <span
                key={i}
                className={`w-2 h-2 rounded-full transition-all ${
                  i === currentStepIndex ? 'w-4 bg-brand-400' : 'bg-slate-700'
                }`}
              />
            ))}
          </div>

          <button
            onClick={handleNext}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-semibold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-md shadow-brand-500/20"
          >
            <span>{isLast ? 'Complete Tour' : 'Next'}</span>
            <ArrowRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};

