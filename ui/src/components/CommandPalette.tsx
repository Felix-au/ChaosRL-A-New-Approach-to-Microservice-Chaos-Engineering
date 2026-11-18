import React, { useState, useEffect, useMemo, useRef } from 'react';
import MiniSearch from 'minisearch';
import { Search, FileText, Compass, Cpu, X, ArrowRight } from 'lucide-react';
import { SearchDocEntry, TabId } from '../types';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  docsIndex: SearchDocEntry[];
  onNavigateTab: (tabId: TabId) => void;
  onOpenDoc: (docPath: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  docsIndex,
  onNavigateTab,
  onOpenDoc
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize MiniSearch engine
  const miniSearch = useMemo(() => {
    if (!docsIndex.length) return null;
    const ms = new MiniSearch({
      fields: ['title', 'section', 'content', 'category'],
      storeFields: ['title', 'section', 'snippet', 'rel_path', 'category'],
      searchOptions: {
        boost: { title: 3, section: 2 },
        fuzzy: 0.2,
        prefix: true
      }
    });
    ms.addAll(docsIndex);
    return ms;
  }, [docsIndex]);

  // Quick navigation destinations
  const quickTabs: Array<{ id: TabId; label: string; desc: string }> = [
    { id: 'overview', label: 'Overview', desc: 'Project architecture, hook, failure cascade' },
    { id: 'approach', label: 'Approach', desc: 'Simulator physics, calibration, Gym env' },
    { id: 'methods', label: 'Methods', desc: '12 candidate pool, 5 families, freeze specs' },
    { id: 'results', label: 'Results', desc: 'Scale-100 discovery curves, leaderboard, stats' },
    { id: 'efficiency', label: 'Efficiency & Generalization', desc: 'Budget sweep, scaling, mesh transfer' },
    { id: 'safety', label: 'Safety & Cost', desc: 'SLO damage trade-offs, Pareto curve, compute' },
    { id: 'original_vs_audited', label: 'Original vs. Audited', desc: 'Pre-audit n=10 vs post-audit n=30 comparison' },
    { id: 'insights', label: 'Insights', desc: 'TreeRanker vs Deep RL, feature importance, ablations' },
    { id: 'rigor', label: 'Rigor & Reproducibility', desc: 'Cryptographic manifests, access logs, reproduction' },
    { id: 'docs', label: 'Docs Library', desc: 'Complete research papers, audit reports, and postmortem' }
  ];

  // Perform search
  const results = useMemo(() => {
    if (!query.trim()) {
      return quickTabs.map((t) => ({
        type: 'tab',
        id: t.id,
        title: t.label,
        snippet: t.desc,
        category: 'Navigation'
      }));
    }

    // Filter tabs first
    const matchedTabs = quickTabs
      .filter((t) => t.label.toLowerCase().includes(query.toLowerCase()) || t.desc.toLowerCase().includes(query.toLowerCase()))
      .map((t) => ({
        type: 'tab',
        id: t.id,
        title: `Tab: ${t.label}`,
        snippet: t.desc,
        category: 'Navigation'
      }));

    // Query MiniSearch docs
    let docMatches: any[] = [];
    if (miniSearch) {
      const searchRes = miniSearch.search(query);
      docMatches = searchRes.slice(0, 8).map((r: any) => ({
        type: 'doc',
        id: r.id,
        title: r.title,
        snippet: r.snippet,
        rel_path: r.rel_path,
        category: r.category
      }));
    }

    return [...matchedTabs, ...docMatches];
  }, [query, miniSearch]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setSelectedIndex(0);
    } else {
      setQuery('');
    }
  }, [isOpen]);

  // Handle keyboard arrow navigation & enter
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev < results.length - 1 ? prev + 1 : 0));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1));
      } else if (e.key === 'Enter' && results[selectedIndex]) {
        e.preventDefault();
        handleSelect(results[selectedIndex]);
      } else if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex]);

  const handleSelect = (item: any) => {
    if (item.type === 'tab') {
      onNavigateTab(item.id);
    } else if (item.type === 'doc') {
      onOpenDoc(item.rel_path);
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl overflow-hidden flex flex-col max-h-[75vh]">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-800 bg-slate-950/60">
          <Search size={18} className="text-slate-400 mr-3" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Search documentation, methods, tables, or jump to tab... (ESC to close)"
            className="w-full bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none"
          />
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-200 rounded">
            <X size={16} />
          </button>
        </div>

        {/* Results List */}
        <div className="overflow-y-auto p-2 space-y-1">
          {results.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">No matching documents or tabs found.</div>
          ) : (
            results.map((item, idx) => (
              <div
                key={idx}
                onClick={() => handleSelect(item)}
                onMouseEnter={() => setSelectedIndex(idx)}
                className={`flex items-start gap-3 p-3 rounded-xl cursor-pointer transition-colors ${
                  idx === selectedIndex ? 'bg-brand-500/15 border border-brand-500/30' : 'hover:bg-slate-800/50 border border-transparent'
                }`}
              >
                <div className="mt-0.5 p-1.5 rounded-lg bg-slate-800 text-slate-300">
                  {item.type === 'tab' ? <Compass size={15} className="text-brand-400" /> : <FileText size={15} className="text-sky-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-100 truncate">{item.title}</span>
                    <span className="text-[10px] font-mono uppercase text-slate-500 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                      {item.category}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-0.5">{item.snippet}</p>
                </div>
                {idx === selectedIndex && <ArrowRight size={14} className="text-brand-400 self-center shrink-0" />}
              </div>
            ))
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-4 py-2 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
          <span>Navigate with <kbd className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-300">↑</kbd> <kbd className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-300">↓</kbd></span>
          <span>Select with <kbd className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-300">Enter</kbd></span>
        </div>
      </div>
    </div>
  );
};

