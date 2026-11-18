import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, ArrowLeft, ArrowRight, Minimize2, FileText, Sun, Moon } from 'lucide-react';
import { TabId } from '../types';

interface PresentationOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: TabId;
  onNavigateTab: (tabId: TabId) => void;
}

const PRESENTATION_SLIDES: Array<{ id: TabId; title: string; subtitle: string; notes: string }> = [
  {
    id: 'overview',
    title: 'ChaosRL: Autonomous Microservice Chaos Engineering',
    subtitle: 'Replacing Random Instance Termination with Reinforcement Learning',
    notes: 'Key talking points: Microservices fail via cascading propagation. Netflix Chaos Monkey kills random instances without memory or multi-fault capability. ChaosRL introduces learned, goal-oriented fault injection.'
  },
  {
    id: 'approach',
    title: 'Empirical Calibration & High-Speed Gym Simulator',
    subtitle: '12,000 steps/sec vector environment grounded in real trace data',
    notes: 'Key talking points: Calibrated on Train-Ticket and Sock-Shop traces. Log-normal latency, cascading timeouts, retry storms, and discrete weakness injection.'
  },
  {
    id: 'methods',
    title: 'Algorithm Pool & Top-5 Cryptographic Freeze',
    subtitle: '12 algorithms across 5 distinct paradigms evaluated',
    notes: 'Key talking points: Spans Deep RL, Graph Neural Networks, Contextual Bandits, and Tabular Trees. Top-5 frozen into immutable SHA-256 manifest before evaluation.'
  },
  {
    id: 'results',
    title: 'Scale-100 Headline Evaluation Results',
    subtitle: 'TreeRanker achieves 2.38× AUDC over Chaos Monkey (p = 0.0037, n=30)',
    notes: 'Key talking points: TreeRanker beats Chaos Monkey with high statistical significance (Wilcoxon adjusted p=0.0037, power 96.1%). Heuristic Expert remains strong benchmark.'
  },
  {
    id: 'efficiency',
    title: 'Sample Efficiency & Low-Budget Performance',
    subtitle: '7.0× faster discovery at B=25 steps; scale testing up to N=500',
    notes: 'Key talking points: In low-budget CI/CD runs (B=25), learned agents find weaknesses early while random baselines hit zero. Maintains superiority at N=20 and N=500.'
  },
  {
    id: 'safety',
    title: 'Multi-Fault Collateral Damage & Safety Trade-offs',
    subtitle: '53.3× safer than unconstrained all-fault exploration',
    notes: 'Key talking points: Clarify damage metric skew—Chaos Monkey only terminates pods. Compared to Random-All which tests the same multi-fault space, ChaosRL is 53x safer.'
  },
  {
    id: 'original_vs_audited',
    title: 'Independent Audit & Statistical Tripling',
    subtitle: 'Tripled evaluation cohort from n=10 to n=30 confirms core thesis',
    notes: 'Key talking points: Pre-audit n=10 showed directional trend (p=0.121). Post-audit n=30 confirmed statistical significance (p=0.0037), turning a hypothesis into hard evidence.'
  },
  {
    id: 'insights',
    title: 'Why Did Tabular Trees Beat Deep RL?',
    subtitle: 'Discrete topological inductive priors outperform deep policy approximations',
    notes: 'Key talking points: Graph centrality and telemetry gradients provide non-stationary priors that decision tree rankers exploit with zero sample efficiency lag.'
  },
  {
    id: 'rigor',
    title: 'Audit Trail, Reproducibility & Verification',
    subtitle: '104 passing tests, 0 data leakage violations, full replication suite',
    notes: 'Key talking points: Cryptographic freeze manifest, immutable test access log, and single-command CLI reproduction verify absolute scientific integrity.'
  }
];

export const PresentationOverlay: React.FC<PresentationOverlayProps> = ({
  isOpen,
  onClose,
  activeTab,
  onNavigateTab
}) => {
  const [seconds, setSeconds] = useState(0);
  const [timerRunning, setTimerRunning] = useState(true);
  const [showNotes, setShowNotes] = useState(false);
  const [projectorMode, setProjectorMode] = useState(false);

  // Timer tick
  useEffect(() => {
    let interval: any = null;
    if (isOpen && timerRunning) {
      interval = setInterval(() => {
        setSeconds((s) => s + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isOpen, timerRunning]);

  const currentSlideIndex = Math.max(
    0,
    PRESENTATION_SLIDES.findIndex((s) => s.id === activeTab)
  );
  const currentSlide = PRESENTATION_SLIDES[currentSlideIndex] || PRESENTATION_SLIDES[0];

  const handleNext = () => {
    if (currentSlideIndex < PRESENTATION_SLIDES.length - 1) {
      onNavigateTab(PRESENTATION_SLIDES[currentSlideIndex + 1].id);
    }
  };

  const handlePrev = () => {
    if (currentSlideIndex > 0) {
      onNavigateTab(PRESENTATION_SLIDES[currentSlideIndex - 1].id);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
        e.preventDefault();
        handleNext();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault();
        handlePrev();
      } else if (e.key === 'Escape') {
        onClose();
      } else if (e.key.toLowerCase() === 'n') {
        setShowNotes((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, currentSlideIndex]);

  if (!isOpen) return null;

  const formatTimer = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div
      className={`fixed top-0 left-0 right-0 z-40 px-6 py-2.5 flex items-center justify-between border-b shadow-2xl backdrop-blur-md transition-all ${
        projectorMode
          ? 'bg-slate-900 border-brand-400 text-white'
          : 'bg-slate-950/95 border-slate-800 text-slate-100'
      }`}
    >
      {/* Slide Title */}
      <div className="flex items-center gap-3">
        <span className="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/40 text-xs font-mono font-bold">
          SLIDE {currentSlideIndex + 1} / {PRESENTATION_SLIDES.length}
        </span>
        <div>
          <h2 className="text-sm font-bold text-slate-100 truncate max-w-md">{currentSlide.title}</h2>
          <p className="text-[11px] text-slate-400 truncate max-w-md">{currentSlide.subtitle}</p>
        </div>
      </div>

      {/* Presenter Controls */}
      <div className="flex items-center gap-4">
        {/* Timer */}
        <div className="flex items-center gap-2 bg-slate-900 px-3 py-1 rounded-lg border border-slate-800 text-xs font-mono">
          <span className="text-brand-400 font-bold">{formatTimer(seconds)}</span>
          <button
            onClick={() => setTimerRunning(!timerRunning)}
            className="text-slate-400 hover:text-slate-200"
            title={timerRunning ? 'Pause timer' : 'Resume timer'}
          >
            {timerRunning ? <Pause size={12} /> : <Play size={12} />}
          </button>
          <button
            onClick={() => setSeconds(0)}
            className="text-slate-400 hover:text-slate-200"
            title="Reset timer"
          >
            <RotateCcw size={12} />
          </button>
        </div>

        {/* Presenter Notes Toggle */}
        <button
          onClick={() => setShowNotes(!showNotes)}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors ${
            showNotes
              ? 'bg-brand-500/20 text-brand-300 border-brand-500/40'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
          }`}
          title="Toggle Presenter Notes (N)"
        >
          <FileText size={13} />
          <span>Notes</span>
        </button>

        {/* Projector Mode */}
        <button
          onClick={() => setProjectorMode(!projectorMode)}
          className={`p-1.5 rounded-lg border text-xs transition-colors ${
            projectorMode
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
          }`}
          title="Toggle Projector Contrast Mode"
        >
          {projectorMode ? <Sun size={14} /> : <Moon size={14} />}
        </button>

        {/* Slide Navigation */}
        <div className="flex items-center gap-1">
          <button
            onClick={handlePrev}
            disabled={currentSlideIndex === 0}
            className={`p-1.5 rounded border ${
              currentSlideIndex === 0
                ? 'text-slate-700 border-slate-900 cursor-not-allowed'
                : 'text-slate-300 border-slate-800 hover:bg-slate-800'
            }`}
            title="Previous slide (Left Arrow)"
          >
            <ArrowLeft size={14} />
          </button>
          <button
            onClick={handleNext}
            disabled={currentSlideIndex === PRESENTATION_SLIDES.length - 1}
            className={`p-1.5 rounded border ${
              currentSlideIndex === PRESENTATION_SLIDES.length - 1
                ? 'text-slate-700 border-slate-900 cursor-not-allowed'
                : 'text-slate-300 border-slate-800 hover:bg-slate-800'
            }`}
            title="Next slide (Right Arrow)"
          >
            <ArrowRight size={14} />
          </button>
        </div>

        {/* Exit Presentation */}
        <button
          onClick={onClose}
          className="flex items-center gap-1.5 px-3 py-1 bg-rose-950/60 hover:bg-rose-900 text-rose-300 border border-rose-800/80 rounded-lg text-xs font-semibold transition-colors"
          title="Exit Presentation Mode (ESC)"
        >
          <Minimize2 size={13} />
          <span>Exit</span>
        </button>
      </div>

      {/* Presenter Notes Float Box */}
      {showNotes && (
        <div className="fixed top-16 right-6 z-50 w-80 p-4 rounded-xl border border-brand-500/40 bg-slate-900/95 shadow-2xl backdrop-blur-md animate-fade-in text-xs space-y-2">
          <div className="flex items-center justify-between font-bold text-brand-300 border-b border-slate-800 pb-1.5">
            <span>Presenter Notes</span>
            <span className="text-[10px] text-slate-500">Shortcut: N</span>
          </div>
          <p className="text-slate-300 leading-relaxed">{currentSlide.notes}</p>
        </div>
      )}
    </div>
  );
};

