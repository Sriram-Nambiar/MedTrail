import React from 'react';
import type { GraphNode } from '../types/graph';
import { X, ExternalLink, AlertTriangle, ShieldCheck } from 'lucide-react';

interface EntityInspectorProps {
  node: GraphNode | null;
  onClose: () => void;
}

export const EntityInspector: React.FC<EntityInspectorProps> = ({ node, onClose }) => {
  if (!node) return null;

  const p = node.properties || {};

  // Determine external URL if applicable
  const getExternalLink = () => {
    if (p.source_url) return p.source_url;
    if (p.pmid) return `https://pubmed.ncbi.nlm.nih.gov/${p.pmid}/`;
    if (p.nct_id) return `https://clinicaltrials.gov/study/${p.nct_id}`;
    if (p.chembl_id) return `https://www.ebi.ac.uk/chembl/compound_report_card/${p.chembl_id}/`;
    if (p.accession) return `https://www.uniprot.org/uniprotkb/${p.accession}/entry`;
    if (p.mondo_id) return `https://monarchinitiative.org/disease/${p.mondo_id}`;
    return null;
  };

  const extUrl = getExternalLink();

  // Tier label helper
  const getTierBadge = (tier?: number) => {
    if (!tier) return null;
    const tierMap: Record<number, { label: string; desc: string }> = {
      1: { label: 'Tier 1', desc: 'Clinical Trial Evidence (Reported Outcomes)' },
      2: { label: 'Tier 2', desc: 'Observational Human Evidence' },
      3: { label: 'Tier 3', desc: 'Preclinical Evidence (Cell / Animal Models)' },
      4: { label: 'Tier 4', desc: 'Mechanistic / Database Association Only' },
    };
    const t = tierMap[tier] || { label: `Tier ${tier}`, desc: 'Evidence' };
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
        <ShieldCheck size={13} />
        <span>{t.label}: {t.desc}</span>
      </div>
    );
  };

  // Direction badge
  const getDirectionBadge = (dir?: string) => {
    if (!dir) return null;
    const isSupport = dir.toLowerCase() === 'supports';
    const isNoEffect = dir.toLowerCase() === 'no_effect';
    return (
      <span
        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
          isSupport
            ? 'bg-emerald-100 text-emerald-800'
            : isNoEffect
            ? 'bg-rose-100 text-rose-800'
            : 'bg-amber-100 text-amber-800'
        }`}
      >
        {isSupport ? 'Direction: Supports' : isNoEffect ? 'Direction: No Clinical Effect' : `Direction: ${dir}`}
      </span>
    );
  };

  return (
    <div className="absolute top-4 right-4 w-96 max-w-[calc(100vw-32px)] bg-white/95 backdrop-blur-md border border-slate-200 rounded-xl shadow-lg p-5 z-20 overflow-y-auto max-h-[calc(100%-32px)] text-sm animate-in fade-in slide-in-from-right-4 duration-150">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 pb-3 border-b border-slate-100">
        <div>
          <span
            className="inline-block px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider rounded mb-1 text-white"
            style={{ backgroundColor: node.color }}
          >
            {node.type}
          </span>
          <h3 className="font-bold text-slate-900 text-base leading-tight">
            {node.label}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100 transition"
          title="Close details"
        >
          <X size={16} />
        </button>
      </div>

      <div className="space-y-4 pt-3 text-slate-700">
        {/* Badges for Evidence nodes */}
        {node.type === 'Evidence' && (
          <div className="flex flex-col gap-2">
            {getTierBadge(p.tier)}
            {getDirectionBadge(p.direction)}
          </div>
        )}

        {/* Drug mechanism / approval */}
        {node.type === 'Drug' && (
          <div className="space-y-2">
            {p.approval_status && (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <div className="text-xs text-slate-500 font-medium">Regulatory Status</div>
                <div className="text-xs font-semibold text-slate-800 mt-0.5">{p.approval_status}</div>
              </div>
            )}
            {p.mechanism && (
              <div>
                <div className="text-xs text-slate-500 font-medium">Mechanism of Action</div>
                <div className="text-xs text-slate-800 mt-0.5 leading-relaxed">{p.mechanism}</div>
              </div>
            )}
            {p.brand_names && p.brand_names.length > 0 && (
              <div className="text-xs text-slate-500">
                Brands: <span className="font-medium text-slate-700">{p.brand_names.join(', ')}</span>
              </div>
            )}
          </div>
        )}

        {/* Clinical Study details */}
        {node.type === 'ClinicalStudy' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="text-amber-700">{p.phase || 'Trial'}</span>
              <span className="text-slate-500">Status: {p.status || 'Completed'}</span>
            </div>
            {p.intervention && (
              <div className="text-xs bg-slate-50 p-2 rounded border border-slate-200">
                <span className="font-semibold text-slate-700">Intervention: </span>
                {p.intervention}
              </div>
            )}
            {p.results_summary && (
              <div>
                <div className="text-xs font-semibold text-slate-800 mb-1">Trial Results Summary</div>
                <p className="text-xs leading-relaxed text-slate-600 bg-amber-50/50 p-2.5 rounded border border-amber-100">
                  {p.results_summary}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Evidence details */}
        {node.type === 'Evidence' && (
          <div className="space-y-3">
            {p.summary && (
              <div>
                <div className="text-xs font-semibold text-slate-800 mb-1">Evidence Summary</div>
                <p className="text-xs leading-relaxed text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                  {p.summary}
                </p>
              </div>
            )}
            {p.limitations && (
              <div>
                <div className="text-xs font-semibold text-rose-700 flex items-center gap-1 mb-1">
                  <AlertTriangle size={13} />
                  Documented Limitations
                </div>
                <p className="text-xs leading-relaxed text-rose-800 bg-rose-50/70 p-2.5 rounded-lg border border-rose-200">
                  {p.limitations}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Research Paper details */}
        {node.type === 'ResearchPaper' && (
          <div className="space-y-2">
            <div className="text-xs text-slate-500 font-medium">
              {p.journal} • {p.pub_date}
            </div>
            {p.abstract && (
              <div>
                <div className="text-xs font-semibold text-slate-800 mb-1">Abstract</div>
                <p className="text-xs text-slate-600 leading-relaxed max-h-40 overflow-y-auto pr-1">
                  {p.abstract}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Pathway / Target details */}
        {(node.type === 'Pathway' || node.type === 'Protein' || node.type === 'Gene') && (
          <div className="space-y-2 text-xs">
            {p.function && (
              <div>
                <span className="font-semibold text-slate-700">Biological Function:</span>
                <p className="text-slate-600 mt-0.5 leading-relaxed">{p.function}</p>
              </div>
            )}
            {p.biological_role && (
              <div>
                <span className="font-semibold text-slate-700">Role in Fibrosis:</span>
                <p className="text-slate-600 mt-0.5 leading-relaxed">{p.biological_role}</p>
              </div>
            )}
            {p.accession && (
              <div className="text-slate-500">
                UniProt Accession: <span className="font-mono text-slate-800">{p.accession}</span>
              </div>
            )}
          </div>
        )}

        {/* Side Effect details */}
        {node.type === 'SideEffect' && (
          <div className="space-y-1 text-xs">
            {p.severity && (
              <div>
                Severity: <span className="font-semibold text-rose-700">{p.severity}</span>
              </div>
            )}
            {p.umls_cui && (
              <div className="text-slate-500">
                UMLS CUI: <span className="font-mono text-slate-700">{p.umls_cui}</span>
              </div>
            )}
          </div>
        )}

        {/* External Link button */}
        {extUrl && (
          <div className="pt-2 border-t border-slate-100">
            <a
              href={extUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-800 hover:underline font-medium"
            >
              <span>View Source Record</span>
              <ExternalLink size={12} />
            </a>
          </div>
        )}

        {/* Unverified Hypothesis Disclaimer */}
        <div className="text-[11px] text-slate-600 bg-slate-100/80 p-2 rounded border border-slate-200 flex items-start gap-1.5">
          <AlertTriangle size={13} className="text-amber-500 shrink-0 mt-0.5" />
          <span>
            <strong>Exploratory Research Tool:</strong> Graph paths indicate indirect biological relationships, not proof of clinical safety or therapeutic efficacy.
          </span>
        </div>
      </div>
    </div>
  );
};
