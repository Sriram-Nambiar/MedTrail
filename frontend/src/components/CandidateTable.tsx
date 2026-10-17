import React from 'react';
import type { CandidateDrug } from '../types/graph';
import { ShieldCheck, AlertCircle, ArrowRight } from 'lucide-react';

interface CandidateTableProps {
  candidates: CandidateDrug[];
  onSelectCandidate: (drugName: string) => void;
}

export const CandidateTable: React.FC<CandidateTableProps> = ({
  candidates,
  onSelectCandidate,
}) => {
  const getTierBadge = (tier: number) => {
    switch (tier) {
      case 1:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <ShieldCheck size={12} /> Tier 1: Clinical Trial
          </span>
        );
      case 2:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
            Tier 2: Observational
          </span>
        );
      case 3:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
            Tier 3: Preclinical
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            Tier 4: Mechanistic
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-slate-900 text-sm">
            Idiopathic Pulmonary Fibrosis — Transparent Candidate Ranking
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Ranked by highest evidence tier first, then independent sources. Negative findings are never hidden.
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <th className="py-3 px-4 w-12 text-center">Rank</th>
              <th className="py-3 px-4">Medicine</th>
              <th className="py-3 px-4">Best Evidence Tier</th>
              <th className="py-3 px-4">Evidence Direction</th>
              <th className="py-3 px-4">Key Targets</th>
              <th className="py-3 px-4">Reported Side Effects</th>
              <th className="py-3 px-4">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {candidates.map((cand, idx) => {
              const hasNegative = cand.negative_evidence_count > 0;
              const hasSupport = cand.supporting_evidence_count > 0;

              return (
                <tr key={cand.drug_id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 px-4 text-center font-mono font-medium text-slate-400">
                    {idx + 1}
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-900">
                    <div className="font-semibold text-sm">{cand.drug_name}</div>
                    <div className="text-[11px] text-slate-500 line-clamp-1">{cand.approval_status}</div>
                  </td>
                  <td className="py-3 px-4">
                    {getTierBadge(cand.best_tier)}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {hasSupport && (
                        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          +{cand.supporting_evidence_count} Supporting
                        </span>
                      )}
                      {hasNegative && (
                        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 flex items-center gap-1">
                          <AlertCircle size={10} /> -{cand.negative_evidence_count} No Effect
                        </span>
                      )}
                      {!hasSupport && !hasNegative && (
                        <span className="text-slate-400 text-[11px]">No formal trial</span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1 flex-wrap">
                      {cand.targets.map((tgt) => (
                        <span key={tgt} className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-mono text-[10px]">
                          {tgt}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-slate-600 max-w-xs">
                    {cand.side_effects && cand.side_effects.length > 0 ? (
                      <span className="line-clamp-1">{cand.side_effects.slice(0, 3).join(', ')}</span>
                    ) : (
                      <span className="text-slate-400 italic">None recorded</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <button
                      onClick={() => onSelectCandidate(cand.drug_name)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition"
                    >
                      <span>Explore</span>
                      <ArrowRight size={12} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
