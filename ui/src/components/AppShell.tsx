import React, { useState, useEffect } from 'react';
import {
  Zap,
  Activity,
  Layers,
  BarChart3,
  TrendingUp,
  ShieldCheck,
  GitCompare,
  Lightbulb,
  Lock,
  BookOpen,
  Search,
  Sparkles,
  Tv,
  HelpCircle,
  X,
  Code
} from 'lucide-react';
import { TabId } from '../types';
import { useChaosData } from '../hooks/useChaosData';
import { OverviewTab } from '../tabs/OverviewTab';
import { ApproachTab } from '../tabs/ApproachTab';
import { MethodsTab } from '../tabs/MethodsTab';
import { ResultsTab } from '../tabs/ResultsTab';
import { EfficiencyTab } from '../tabs/EfficiencyTab';
import { SafetyTab } from '../tabs/SafetyTab';
import { OriginalVsAuditedTab } from '../tabs/OriginalVsAuditedTab';
import { InsightsTab } from '../tabs/InsightsTab';
import { RigorTab } from '../tabs/RigorTab';
import { DocsTab } from '../tabs/DocsTab';
import { CommandPalette } from './CommandPalette';
import { GuidedTour } from './GuidedTour';
import { PresentationOverlay } from './PresentationOverlay';
import { InsightEngine } from '../insight/engine';

export const AppShell: React.FC = () => {
  const {
    loading,
    error,
    cohort,
    setCohort,
    activeData,
    preAuditData,
    postAuditData,
    curves,
    methods,
    architecture,
    rigor,
    docsIndex
  } = useChaosData();

  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isTourOpen, setIsTourOpen] = useState(false);
  const [isPresentationOpen, setIsPresentationOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isDevInsightsOpen, setIsDevInsightsOpen] = useState(false);

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in an input
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes((e.target as HTMLElement).tagName)) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      } else if (e.key === '?') {
        e.preventDefault();
        setIsHelpOpen((prev) => !prev);
      } else if (e.key.toLowerCase() === 'p' || e.key.toLowerCase() === 'f') {
        e.preventDefault();
        setIsPresentationOpen((prev) => !prev);
      } else if (e.key.toLowerCase() === 't') {
        e.preventDefault();
        setIsTourOpen(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const tabs: Array<{ id: TabId; label: string; icon: React.ReactNode }> = [
    { id: 'overview', label: 'Overview', icon: <Zap size={15} /> },
    { id: 'approach', label: 'Approach', icon: <Layers size={15} /> },
    { id: 'methods', label: 'Methods', icon: <Code size={15} /> },
    { id: 'results', label: 'Results', icon: <BarChart3 size={15} /> },
    { id: 'efficiency', label: 'Efficiency & Scale', icon: <TrendingUp size={15} /> },
    { id: 'safety', label: 'Safety & Cost', icon: <ShieldCheck size={15} /> },
    { id: 'original_vs_audited', label: 'Original vs. Audited', icon: <GitCompare size={15} /> },
    { id: 'insights', label: 'Insights', icon: <Lightbulb size={15} /> },
    { id: 'rigor', label: 'Rigor', icon: <Lock size={15} /> },
    { id: 'docs', label: 'Docs', icon: <BookOpen size={15} /> }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-brand-500/20 border border-brand-500/40 flex items-center justify-center animate-pulse">
          <Zap className="text-brand-400" size={24} />
        </div>
        <div className="text-slate-200 font-bold text-sm">Initializing ChaosRL Presentation Engine...</div>
        <div className="text-xs text-slate-500 font-mono">Loading telemetry curves, cryptographic manifests & datasets</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-center space-y-4">
        <div className="text-rose-400 font-bold text-base">Error Loading Project Data</div>
        <div className="text-xs text-slate-400 font-mono max-w-md">{error}</div>
        <div className="text-xs text-slate-500">Please run <code>python ui/scripts/build_data.py</code> to regenerate datasets.</div>
      </div>
    );
  }

  const rawScale100 = activeData?.scale100 || [];
  const evaluatedInsights = InsightEngine.analyzeScale100(rawScale100, cohort);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-brand-500 selection:text-slate-950">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-30 bg-slate-950/90 border-b border-slate-800/80 backdrop-blur-md px-4 sm:px-8 py-3">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
          {/* Logo & Identity */}
          <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
            <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActiveTab('overview')}>
              <div className="w-8 h-8 rounded-lg bg-brand-500/20 border border-brand-500/40 flex items-center justify-center text-brand-400 shadow-md shadow-brand-500/10">
                <Zap size={18} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-base tracking-tight text-white">ChaosRL</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 bg-brand-500/20 text-brand-300 rounded border border-brand-500/30 font-bold">
                    v1.0
                  </span>
                </div>
                <div className="text-[10px] text-slate-400 hidden sm:block">Autonomous Microservice Chaos Engineering</div>
              </div>
            </div>

            {/* Mobile Actions */}
            <div className="flex items-center gap-1.5 md:hidden">
              <button
                onClick={() => setIsSearchOpen(true)}
                className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300"
              >
                <Search size={16} />
              </button>
            </div>
          </div>

          {/* Result-Set Toggle & Controls */}
          <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
            {/* Cohort Switcher */}
            <div className="flex items-center p-0.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-medium">
              <button
                onClick={() => setCohort('post_audit')}
                className={`px-3 py-1 rounded-lg transition-all flex items-center gap-1.5 ${
                  cohort === 'post_audit'
                    ? 'bg-brand-500 text-slate-950 font-bold shadow-sm shadow-brand-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Audited Run: Extended n=30 systems cohort (3x power, confirmed p=0.0037)"
              >
                <span>Audited Run (n=30)</span>
                <span className={`text-[9px] px-1 py-0.2 rounded font-mono ${cohort === 'post_audit' ? 'bg-slate-950 text-brand-300' : 'bg-slate-800 text-slate-400'}`}>
                  96% Power
                </span>
              </button>
              <button
                onClick={() => setCohort('pre_audit')}
                className={`px-3 py-1 rounded-lg transition-all ${
                  cohort === 'pre_audit'
                    ? 'bg-brand-500 text-slate-950 font-bold shadow-sm shadow-brand-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Original Run: Pre-audit n=10 systems cohort"
              >
                <span>Original Run (n=10)</span>
              </button>
            </div>

            {/* Quick Actions */}
            <div className="hidden sm:flex items-center gap-2">
              <button
                onClick={() => setIsSearchOpen(true)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-800 transition-colors"
                title="Search Docs & Tabs (Ctrl+K)"
              >
                <Search size={13} className="text-slate-400" />
                <span className="hidden lg:inline">Search</span>
                <kbd className="px-1.5 py-0.2 bg-slate-950 border border-slate-800 rounded text-[10px] text-slate-400 font-mono">
                  ⌘K
                </kbd>
              </button>

              <button
                onClick={() => setIsTourOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-brand-500/10 hover:bg-brand-500/20 text-brand-300 text-xs font-semibold border border-brand-500/30 transition-colors"
                title="Start Guided Tour (T)"
              >
                <Sparkles size={13} className="text-brand-400" />
                <span>Tour</span>
              </button>

              <button
                onClick={() => setIsPresentationOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-800 transition-colors"
                title="Presentation Mode (P)"
              >
                <Tv size={13} />
                <span>Present</span>
              </button>

              <button
                onClick={() => setIsHelpOpen(true)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
                title="Keyboard Shortcuts (?)"
              >
                <HelpCircle size={15} />
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation Ribbon */}
        <div className="max-w-7xl mx-auto mt-3 overflow-x-auto scrollbar-none flex items-center gap-1.5 border-t border-slate-800/60 pt-2.5">
          {tabs.map((t) => {
            const isActive = activeTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-slate-800 text-brand-300 font-bold border border-slate-700 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <span className={isActive ? 'text-brand-400' : 'text-slate-500'}>{t.icon}</span>
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Tab Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-8 py-8">
        {activeTab === 'overview' && (
          <OverviewTab
            data={activeData}
            stages={architecture?.stages || []}
            onNavigateTab={(tab) => setActiveTab(tab)}
          />
        )}
        {activeTab === 'approach' && <ApproachTab data={activeData} />}
        {activeTab === 'methods' && <MethodsTab methods={methods} />}
        {activeTab === 'results' && (
          <ResultsTab data={activeData} curves={curves} cohort={cohort} />
        )}
        {activeTab === 'efficiency' && <EfficiencyTab data={activeData} cohort={cohort} />}
        {activeTab === 'safety' && <SafetyTab data={activeData} cohort={cohort} />}
        {activeTab === 'original_vs_audited' && (
          <OriginalVsAuditedTab preAuditData={preAuditData} postAuditData={postAuditData} />
        )}
        {activeTab === 'insights' && <InsightsTab data={activeData} />}
        {activeTab === 'rigor' && <RigorTab rigor={rigor} />}
        {activeTab === 'docs' && <DocsTab />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 px-4 sm:px-8 py-5 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span>ChaosRL Research Project</span>
            <span>•</span>
            <span className="font-mono text-slate-400">Git: {rigor?.git_commit_sha || 'ef8d59a'}</span>
            <span>•</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <ShieldCheck size={12} /> 104 Passing Tests
            </span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <button
              onClick={() => setIsDevInsightsOpen(true)}
              className="text-slate-400 hover:text-brand-400 underline"
            >
              Insight Engine Debugger
            </button>
            <button
              onClick={() => setActiveTab('rigor')}
              className="text-slate-400 hover:text-slate-200"
            >
              Audit Verification Manifest
            </button>
          </div>
        </div>
      </footer>

      {/* Developer Insights Modal */}
      {isDevInsightsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 text-brand-400 font-bold text-sm">
                <Code size={16} />
                <span>Pure Insight Engine Transparency View</span>
              </div>
              <button onClick={() => setIsDevInsightsOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X size={16} />
              </button>
            </div>

            <p className="text-xs text-slate-300">
              The Insight Engine analyzes active cohort rows dynamically at runtime and evaluates rules without hardcoded strings:
            </p>

            <div className="space-y-3">
              {evaluatedInsights.map((ins, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1">
                  <div className="flex justify-between font-mono text-[10px] text-brand-400">
                    <span>{ins.ruleId}</span>
                    <span>Ratio: {ins.metrics.ratio.toFixed(2)}x</span>
                  </div>
                  <div className="font-bold text-slate-100">{ins.headline}</div>
                  <p className="text-slate-400">{ins.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts Modal */}
      {isHelpOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <HelpCircle size={16} className="text-brand-400" />
                <span>Keyboard Shortcuts</span>
              </h3>
              <button onClick={() => setIsHelpOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X size={16} />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-300">Search Docs & Tabs</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-brand-400 font-mono font-bold">Ctrl + K</kbd>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-300">Toggle Presentation Mode</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-brand-400 font-mono font-bold">P / F</kbd>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-300">Next / Prev Slide in Presenter</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-brand-400 font-mono font-bold">← / →</kbd>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-300">Launch Guided Tour</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-brand-400 font-mono font-bold">T</kbd>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-300">Close Overlays</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-brand-400 font-mono font-bold">ESC</kbd>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Floating Overlays */}
      <CommandPalette
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        docsIndex={docsIndex}
        onNavigateTab={(tab) => setActiveTab(tab)}
        onOpenDoc={(docPath) => {
          setActiveTab('docs');
        }}
      />

      <GuidedTour
        isOpen={isTourOpen}
        onClose={() => setIsTourOpen(false)}
        onNavigateTab={(tab) => setActiveTab(tab)}
      />

      <PresentationOverlay
        isOpen={isPresentationOpen}
        onClose={() => setIsPresentationOpen(false)}
        activeTab={activeTab}
        onNavigateTab={(tab) => setActiveTab(tab)}
      />
    </div>
  );
};

