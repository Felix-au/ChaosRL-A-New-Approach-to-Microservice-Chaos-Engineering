import React, { useState } from 'react';
import { Cpu, Filter, Award, CheckCircle2, ShieldCheck, X, ExternalLink, Zap } from 'lucide-react';
import { MethodMetadata } from '../types';

interface MethodsTabProps {
  methods: MethodMetadata[];
}

export const MethodsTab: React.FC<MethodsTabProps> = ({ methods }) => {
  const [selectedFamily, setSelectedFamily] = useState<string>('all');
  const [activeMethod, setActiveMethod] = useState<MethodMetadata | null>(null);

  const families = ['all', 'Top-5 Frozen', 'Tabular / Tree', 'Deep RL', 'Contextual Bandit', 'Ensemble', 'Baseline'];

  const filteredMethods = methods.filter((m) => {
    if (selectedFamily === 'all') return true;
    if (selectedFamily === 'Top-5 Frozen') return m.is_top5;
    return m.family.toLowerCase().includes(selectedFamily.toLowerCase());
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Intro Banner */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-3">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <Cpu className="text-brand-400" size={22} />
              <span>The ChaosRL Model Pool & Top-5 Candidate Freeze</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-3xl">
              To rigorously test what algorithm paradigm excels at microservice chaos engineering, we evaluated 12 algorithms across 5 distinct paradigms. The top 5 models were selected by multi-objective Pareto efficiency and cryptographically frozen into immutable SHA-256 manifests.
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-950 text-brand-300 border border-slate-800 shrink-0">
            15 Evaluated Models
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5 mr-2">
          <Filter size={14} /> Filter Paradigm:
        </span>
        {families.map((f) => (
          <button
            key={f}
            onClick={() => setSelectedFamily(f)}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              selectedFamily === f
                ? 'bg-brand-500 text-slate-950 font-bold shadow-md shadow-brand-500/20'
                : 'bg-slate-900/80 text-slate-400 border border-slate-800 hover:text-slate-200'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Methods Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredMethods.map((m) => {
          const isWinner = m.id === 'C12';
          return (
            <div
              key={m.id}
              onClick={() => setActiveMethod(m)}
              className={`p-5 rounded-2xl border cursor-pointer transition-all hover:scale-[1.01] flex flex-col justify-between ${
                isWinner
                  ? 'bg-gradient-to-br from-brand-950/40 to-slate-900/90 border-brand-500/50 shadow-lg shadow-brand-500/10'
                  : m.is_top5
                  ? 'bg-slate-900/80 border-slate-700/80 hover:border-brand-500/40'
                  : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800">
                    {m.id}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {isWinner && (
                      <span className="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 text-[10px] font-bold border border-brand-500/40 flex items-center gap-1">
                        <Award size={11} /> Top-1 Champion
                      </span>
                    )}
                    {m.is_top5 && !isWinner && (
                      <span className="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 text-[10px] font-bold border border-sky-500/40">
                        Top-5 Frozen
                      </span>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-100">{m.name}</h3>
                  <span className="text-xs text-brand-400 font-medium">{m.family}</span>
                </div>

                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">{m.description}</p>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>{m.parameters > 0 ? `${m.parameters.toLocaleString()} params` : 'Handcrafted'}</span>
                <span>{m.training_time_s > 0 ? `${m.training_time_s}s train` : '0s (Rule-based)'}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Method Details Modal / Drawer */}
      {activeMethod && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-xl rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-xs font-mono text-brand-400 uppercase font-bold">{activeMethod.family}</span>
                <h3 className="text-lg font-bold text-slate-100">{activeMethod.name}</h3>
              </div>
              <button onClick={() => setActiveMethod(null)} className="p-1 text-slate-400 hover:text-slate-200">
                <X size={18} />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">{activeMethod.description}</p>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Parameters</span>
                <span className="font-mono text-slate-200 font-bold">{activeMethod.parameters.toLocaleString()}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Training Duration</span>
                <span className="font-mono text-slate-200 font-bold">{activeMethod.training_time_s} seconds</span>
              </div>
            </div>

            {/* Hyperparameters */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-200">Hyperparameters & Configuration:</span>
              <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-brand-300 overflow-x-auto">
                {JSON.stringify(activeMethod.hyperparams, null, 2)}
              </pre>
            </div>

            {/* Checkpoint Hash */}
            <div className="space-y-1">
              <span className="text-[11px] font-bold text-slate-300 flex items-center gap-1.5">
                <ShieldCheck size={14} className="text-brand-400" />
                <span>Cryptographic SHA-256 Checkpoint Signature:</span>
              </span>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-400 break-all select-all">
                {activeMethod.frozen_hash}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

