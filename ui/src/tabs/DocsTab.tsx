import React, { useState, useEffect } from 'react';
import { BookOpen, FileText, Download, Search, Check, Folder, ChevronRight, ChevronDown } from 'lucide-react';
import { MarkdownRenderer } from '../markdown/MarkdownRenderer';

interface DocItem {
  id: string;
  name: string;
  path: string;
  category: string;
}

const DOCS_LIST: DocItem[] = [
  // Executive Reports
  { id: 'report', name: 'REPORT.md (Research Report)', path: 'REPORT.md', category: 'Executive Reports' },
  { id: 'readme', name: 'README.md (Project Guide)', path: 'README.md', category: 'Executive Reports' },
  { id: 'audit_report', name: 'audit/REPORT.md (Audit Report)', path: 'audit/REPORT.md', category: 'Executive Reports' },
  { id: 'audit_index', name: 'audit/INDEX.md (Audit Index)', path: 'audit/INDEX.md', category: 'Executive Reports' },
  { id: 'audit_improve', name: 'audit/IMPROVEMENT_SUGGESTIONS.md', path: 'audit/IMPROVEMENT_SUGGESTIONS.md', category: 'Executive Reports' },

  // Research Stages
  { id: 's01', name: 'stage01_hypotheses.md', path: 'docs/stage01_hypotheses.md', category: 'Research Stages' },
  { id: 's02', name: 'stage02_calibration.md', path: 'docs/stage02_calibration.md', category: 'Research Stages' },
  { id: 's03', name: 'stage03_simulator.md', path: 'docs/stage03_simulator.md', category: 'Research Stages' },
  { id: 's04', name: 'stage04_gym_env.md', path: 'docs/stage04_gym_env.md', category: 'Research Stages' },
  { id: 's05', name: 'stage05_baselines.md', path: 'docs/stage05_baselines.md', category: 'Research Stages' },
  { id: 's06', name: 'stage06_candidate_pool.md', path: 'docs/stage06_candidate_pool.md', category: 'Research Stages' },
  { id: 's07', name: 'stage07_training.md', path: 'docs/stage07_training.md', category: 'Research Stages' },
  { id: 's08', name: 'stage08_ensembles.md', path: 'docs/stage08_ensembles.md', category: 'Research Stages' },
  { id: 's09', name: 'stage09_evaluation.md', path: 'docs/stage09_evaluation.md', category: 'Research Stages' },
  { id: 's10', name: 'stage10_postmortem.md', path: 'docs/stage10_postmortem.md', category: 'Research Stages' },

  // Defense & Presentation
  { id: 'qa', name: 'qa_examiner.md (Oral Defense Q&A)', path: 'docs/qa_examiner.md', category: 'Defense & Slides' },
  { id: 'slides', name: 'presentation_outline.md', path: 'docs/presentation_outline.md', category: 'Defense & Slides' }
];

export const DocsTab: React.FC = () => {
  const [selectedDoc, setSelectedDoc] = useState<DocItem>(DOCS_LIST[0]);
  const [docContent, setDocContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    async function loadDoc() {
      try {
        setLoading(true);
        const res = await fetch(`/docs/${selectedDoc.path}`);
        if (!res.ok) throw new Error('Document not found');
        const text = await res.text();
        setDocContent(text);
      } catch (err) {
        setDocContent(`# Document Load Notice\n\nCould not load \`${selectedDoc.path}\` directly. Please ensure \`ui/scripts/build_data.py\` has run.`);
      } finally {
        setLoading(false);
      }
    }
    loadDoc();
  }, [selectedDoc]);

  const handleDownload = () => {
    const blob = new Blob([docContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = selectedDoc.path.split('/').pop() || 'doc.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  const categories = ['Executive Reports', 'Research Stages', 'Defense & Slides'];

  const filteredDocs = DOCS_LIST.filter(
    (d) =>
      d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 animate-fade-in items-start">
      {/* Sidebar Document Tree */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-4 lg:sticky lg:top-24 max-h-[80vh] overflow-y-auto">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-slate-100 font-bold text-sm">
            <BookOpen size={16} className="text-brand-400" />
            <span>Document Repository</span>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-2 text-slate-500" size={13} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter documents..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-2.5 py-1 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-brand-500"
            />
          </div>
        </div>

        <div className="space-y-4 pt-2">
          {categories.map((cat) => {
            const catDocs = filteredDocs.filter((d) => d.category === cat);
            if (!catDocs.length) return null;

            return (
              <div key={cat} className="space-y-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 block">
                  {cat}
                </span>
                <div className="space-y-0.5">
                  {catDocs.map((doc) => {
                    const isSelected = selectedDoc.id === doc.id;
                    return (
                      <button
                        key={doc.id}
                        onClick={() => setSelectedDoc(doc)}
                        className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs text-left transition-colors truncate ${
                          isSelected
                            ? 'bg-brand-500/20 text-brand-300 font-semibold border border-brand-500/30'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                        }`}
                      >
                        <FileText size={13} className={isSelected ? 'text-brand-400' : 'text-slate-500'} />
                        <span className="truncate">{doc.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Document Reading Pane */}
      <div className="lg:col-span-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-8 shadow-xl space-y-6">
        {/* Document Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              {selectedDoc.path}
            </span>
            <h2 className="text-xl font-bold text-slate-100 mt-1">{selectedDoc.name}</h2>
          </div>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <Download size={13} />
            <span>Download MD</span>
          </button>
        </div>

        {/* Content Viewer */}
        {loading ? (
          <div className="py-20 text-center text-xs text-slate-500 font-mono">Loading markdown document...</div>
        ) : (
          <MarkdownRenderer content={docContent} />
        )}
      </div>
    </div>
  );
};

