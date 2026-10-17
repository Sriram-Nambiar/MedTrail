import React from 'react';
import type { KeywordBenchmark } from '../types/graph';
import { GitBranch, Search, CheckCircle2, X } from 'lucide-react';

interface BenchmarkModalProps {
  data: KeywordBenchmark | null;
  onClose: () => void;
}

export const BenchmarkModal: React.FC<BenchmarkModalProps> = ({ data, onClose }) => {
  if (!data) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-3xl w-full max-h-[85vh] overflow-y-auto p-6 space-y-6 text-sm">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              Evaluation Baseline
            </span>
            <h2 className="text-lg font-bold text-slate-900 mt-1">
              Knowledge Graph vs. Keyword Search Comparison
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Demonstrating why multi-hop graph retrieval is essential over naive keyword matching.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 p-1.5 rounded-lg hover:bg-slate-100 transition"
          >
            <X size={18} />
          </button>
        </div>

        {/* Scenario 1 */}
        <div className="space-y-3">
          <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
            <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">1</span>
            {data.scenario_1.title}
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {/* Keyword Search side */}
            <div className="p-3.5 bg-rose-50/50 border border-rose-200 rounded-xl space-y-2">
              <div className="font-semibold text-rose-800 flex items-center gap-1.5">
                <Search size={14} /> Plain PubMed Keyword Search
              </div>
              <div className="font-mono text-[11px] bg-white/80 p-1.5 rounded border border-rose-100 text-slate-700">
                {data.scenario_1.keyword_search.query}
              </div>
              <p className="text-rose-900 leading-relaxed">
                {data.scenario_1.keyword_search.limitation}
              </p>
            </div>

            {/* Graph Traversal side */}
            <div className="p-3.5 bg-emerald-50/50 border border-emerald-200 rounded-xl space-y-2">
              <div className="font-semibold text-emerald-800 flex items-center gap-1.5">
                <GitBranch size={14} /> Neo4j Multi-Hop Retrieval ({data.scenario_1.graph_retrieval.hops} hops)
              </div>
              <ul className="space-y-1 list-disc list-inside text-slate-700">
                {data.scenario_1.graph_retrieval.chain.map((c, i) => (
                  <li key={i} className="leading-snug">{c}</li>
                ))}
              </ul>
              <div className="font-medium text-emerald-900 bg-white/80 p-2 rounded border border-emerald-100 flex items-start gap-1.5">
                <CheckCircle2 size={13} className="text-emerald-600 shrink-0 mt-0.5" />
                <span>{data.scenario_1.graph_retrieval.outcome}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Scenario 2 */}
        <div className="space-y-3 pt-2 border-t border-slate-100">
          <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
            <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">2</span>
            {data.scenario_2.title}
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {/* Keyword Search side */}
            <div className="p-3.5 bg-rose-50/50 border border-rose-200 rounded-xl space-y-2">
              <div className="font-semibold text-rose-800 flex items-center gap-1.5">
                <Search size={14} /> Keyword / Chatbot Search
              </div>
              <p className="text-rose-900 leading-relaxed">
                {data.scenario_2.keyword_search.limitation}
              </p>
            </div>

            {/* Graph Traversal side */}
            <div className="p-3.5 bg-emerald-50/50 border border-emerald-200 rounded-xl space-y-2">
              <div className="font-semibold text-emerald-800 flex items-center gap-1.5">
                <GitBranch size={14} /> Evidence-Tier Stratification
              </div>
              <div className="space-y-1.5 text-slate-700">
                <div className="p-1.5 bg-amber-50 rounded border border-amber-200">
                  <span className="font-semibold text-amber-800">Preclinical (Tier 3): </span>
                  {data.scenario_2.graph_retrieval.evidence_stratification.preclinical.summary}
                </div>
                <div className="p-1.5 bg-rose-50 rounded border border-rose-200">
                  <span className="font-semibold text-rose-800">Human Phase 2 Trial (Tier 1): </span>
                  {data.scenario_2.graph_retrieval.evidence_stratification.clinical_trial.summary}
                </div>
              </div>
              <div className="font-medium text-emerald-900 bg-white/80 p-2 rounded border border-emerald-100 flex items-start gap-1.5">
                <CheckCircle2 size={13} className="text-emerald-600 shrink-0 mt-0.5" />
                <span>{data.scenario_2.graph_retrieval.outcome}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-2 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
          >
            Close Benchmark
          </button>
        </div>
      </div>
    </div>
  );
};
