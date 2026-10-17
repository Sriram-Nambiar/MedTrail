import React from 'react';
import type { CandidateDrug } from '../types/graph';
import { ShieldCheck, AlertTriangle, Activity } from 'lucide-react';

interface CandidateCardProps {
  candidate: CandidateDrug;
  isSelected: boolean;
  onSelect: () => void;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  isSelected,
  onSelect,
}) => {
  const isImatinib = candidate.drug_name === 'Imatinib';
  const isNintedanib = candidate.drug_name === 'Nintedanib';
  const isPamrevlumab = candidate.drug_name === 'Pamrevlumab';

  return (
    <div
      onClick={onSelect}
      className={`bg-white rounded-xl border p-5 transition cursor-pointer shadow-xs ${
        isSelected
          ? 'border-blue-500 ring-2 ring-blue-500/20'
          : 'border-slate-200 hover:border-slate-300 hover:shadow-sm'
      }`}
    >
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-900">{candidate.drug_name}</h3>
            {isNintedanib && (
              <span className="text-[11px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-200">
                FDA Approved for IPF
              </span>
            )}
            {isImatinib && (
              <span className="text-[11px] font-semibold bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full border border-rose-200 flex items-center gap-1">
                <AlertTriangle size={11} /> Phase 2 Ineffective
              </span>
            )}
            {isPamrevlumab && (
              <span className="text-[11px] font-semibold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full border border-amber-200">
                Phase 3 Terminated
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{candidate.approval_status}</p>
        </div>

        {/* Tier badge */}
        <div className="flex items-center gap-1.5 self-start sm:self-auto">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
            <ShieldCheck size={13} /> Tier {candidate.best_tier} Evidence
          </span>
        </div>
      </div>

      {/* Mechanism summary */}
      <div className="pt-3 text-xs text-slate-700 space-y-3">
        <div>
          <span className="font-semibold text-slate-800">Biological Target & Mechanism:</span>
          <p className="text-slate-600 mt-0.5 leading-relaxed">{candidate.mechanism}</p>
        </div>

        {/* Targets chips */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-slate-400 font-medium">Intersected Targets:</span>
          {candidate.targets.map((tgt) => (
            <span
              key={tgt}
              className="px-2 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-100 font-mono text-[11px] font-medium"
            >
              {tgt}
            </span>
          ))}
        </div>

        {/* Conflicting Evidence Callout for Imatinib */}
        {isImatinib && (
          <div className="bg-rose-50 border border-rose-200 rounded-lg p-3 space-y-1.5 text-rose-900">
            <div className="font-bold flex items-center gap-1.5 text-xs text-rose-800">
              <AlertTriangle size={14} className="text-rose-600" />
              Negative Human Outcome (Mechanistic Promise vs Trial Reality)
            </div>
            <p className="text-[11px] leading-relaxed">
              <strong>Preclinical mouse models (Tier 3)</strong> showed antifibrotic collagen reduction by blocking PDGF phosphorylation. However, a randomized Phase 2 trial of 119 human patients (<strong>NCT00130520</strong>) showed <strong>no improvement</strong> in survival or lung capacity decline.
            </p>
          </div>
        )}

        {/* Evidence Findings Breakdown */}
        <div className="space-y-1.5">
          <span className="font-semibold text-slate-800">Key Evidence Records in Graph:</span>
          <div className="space-y-1.5">
            {candidate.evidence_list.map((ev) => (
              <div
                key={ev.id}
                className={`p-2.5 rounded-lg border text-[11px] leading-relaxed ${
                  ev.direction === 'supports'
                    ? 'bg-emerald-50/60 border-emerald-200 text-emerald-950'
                    : 'bg-rose-50/60 border-rose-200 text-rose-950'
                }`}
              >
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span className="capitalize">{ev.type.replace('_', ' ')} (Tier {ev.tier})</span>
                  <span
                    className={`px-1.5 py-0.2 rounded text-[10px] uppercase tracking-wider font-bold ${
                      ev.direction === 'supports'
                        ? 'bg-emerald-200 text-emerald-800'
                        : 'bg-rose-200 text-rose-800'
                    }`}
                  >
                    {ev.direction === 'supports' ? 'Supports' : 'No Effect'}
                  </span>
                </div>
                <p>{ev.summary}</p>
                {ev.limitations && (
                  <div className="text-[10px] mt-1 text-slate-500 italic">
                    Limitation: {ev.limitations}
                  </div>
                )}
                <div className="text-[10px] font-medium text-blue-700 mt-1">
                  Source: {ev.source}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Adverse Events */}
        {candidate.side_effects && candidate.side_effects.length > 0 && (
          <div className="pt-1 flex items-center gap-1.5 text-[11px] text-slate-500">
            <Activity size={13} className="text-slate-400" />
            <span>Documented Adverse Events:</span>
            <span className="font-medium text-slate-700">{candidate.side_effects.join(', ')}</span>
          </div>
        )}
      </div>
    </div>
  );
};
