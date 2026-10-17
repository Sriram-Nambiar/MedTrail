import React, { useState, useEffect } from 'react';
import { Bot, ChevronDown, ChevronUp, CheckCircle2, AlertTriangle } from 'lucide-react';

interface AgentThinkingProps {
  activeDrug: string;
}

interface ThoughtStep {
  step: string;
  detail: string;
  status: 'done' | 'active' | 'warning';
}

const THOUGHT_SCENARIOS: Record<string, { title: string; steps: ThoughtStep[] }> = {
  Nintedanib: {
    title: 'Rediscovering Nintedanib Repurposing for IPF',
    steps: [
      {
        step: '1. Target Discovery',
        detail: 'Traversing IPF disease associations to Receptor Tyrosine Kinase (RTK) signaling cascades (FGFR, PDGF, VEGF pathways).',
        status: 'done',
      },
      {
        step: '2. Multi-Hop Traversal',
        detail: 'Discovered that Nintedanib simultaneously targets FGFR1-3, PDGFRA-B, and KDR (VEGFR2) at low nanomolar IC50 concentrations.',
        status: 'done',
      },
      {
        step: '3. Evidence Provenance',
        detail: 'Retrieved Phase 3 INPULSIS trials (NCT01335464) and NEJM 2014 publication (PMID: 24836310).',
        status: 'done',
      },
      {
        step: '4. Evidence Synthesis',
        detail: 'Tier 1 Clinical Trial confirmed: annual FVC decline reduced by ~50% (-114.7 mL/yr vs -239.9 mL/yr). Gastrointestinal adverse event caveat noted (diarrhea 62.4%).',
        status: 'done',
      },
    ],
  },
  Imatinib: {
    title: 'Evaluating Imatinib — Preserving Conflicting Evidence',
    steps: [
      {
        step: '1. Biological Rationale',
        detail: 'Imatinib selectively blocks PDGF receptors (PDGFRA/B) and c-KIT to prevent pulmonary fibroblast proliferation.',
        status: 'done',
      },
      {
        step: '2. Preclinical Evidence',
        detail: 'Mouse bleomycin models showed antifibrotic collagen reduction (Aono et al. AJRCCM 2005 — Tier 3 Preclinical).',
        status: 'done',
      },
      {
        step: '3. Clinical Trial Verification',
        detail: 'Randomized double-blind Phase 2 trial of 119 human IPF patients (NCT00130520, Daniels et al. AJRCCM 2010).',
        status: 'done',
      },
      {
        step: '4. Conflict Resolution',
        detail: 'CRITICAL: Phase 2 trial showed NO benefit on survival or FVC rate of decline. Animal model promise failed to translate. Hypothesis marked as REFUTED BY TRIAL.',
        status: 'warning',
      },
    ],
  },
  Pirfenidone: {
    title: 'Analyzing Pirfenidone Antifibrotic Pathway',
    steps: [
      {
        step: '1. Target Discovery',
        detail: 'Inspecting TGF-beta receptor signaling, myofibroblast differentiation, and collagen accumulation in IPF.',
        status: 'done',
      },
      {
        step: '2. Mechanism Traversal',
        detail: 'Pirfenidone downregulates TGFB1 synthesis and suppresses downstream collagen synthesis.',
        status: 'done',
      },
      {
        step: '3. Evidence Provenance',
        detail: 'Retrieved Phase 3 ASCEND trial (NCT01366209) and NEJM 2014 publication (PMID: 24836312).',
        status: 'done',
      },
      {
        step: '4. Evidence Synthesis',
        detail: 'Tier 1 Clinical Trial confirmed: 47.9% reduction in proportion of patients with >=10% FVC decline or death. Adverse event noted: photosensitivity rash.',
        status: 'done',
      },
    ],
  },
  Pamrevlumab: {
    title: 'Examining Pamrevlumab Phase 3 Outcome',
    steps: [
      {
        step: '1. Target Identification',
        detail: 'Investigating Connective Tissue Growth Factor (CTGF / CCN2) as a downstream fibrotic driver.',
        status: 'done',
      },
      {
        step: '2. Phase 2 Promise',
        detail: 'Phase 2 PRAISE trial (NCT01890265) suggested attenuation of FVC decline.',
        status: 'done',
      },
      {
        step: '3. Phase 3 ZEPHYRUS-1 Trial',
        detail: 'Phase 3 randomized trial (NCT03955146, Richeldi et al. Eur Respir J 2024).',
        status: 'done',
      },
      {
        step: '4. Trial Outcome',
        detail: 'Failed to meet primary endpoint of FVC change at week 48 vs placebo. IPF program terminated. Demonstrates why rigorous Phase 3 evidence is mandatory.',
        status: 'warning',
      },
    ],
  },
  all: {
    title: 'Global Knowledge Graph Exploration',
    steps: [
      {
        step: '1. Graph Connectivity',
        detail: 'Traversing complete IPF subnetwork: 61 nodes across 10 biological entity types.',
        status: 'done',
      },
      {
        step: '2. Evidence Hierarchy',
        detail: 'Stratifying candidate medicines by transparent evidence tiers (Tier 1 Clinical Trials to Tier 4 Mechanistic).',
        status: 'done',
      },
      {
        step: '3. Integrity & Provenance',
        detail: 'Preserving conflicting evidence side-by-side. Every node is grounded in verified PMIDs, NCT IDs, or UniProt accessions.',
        status: 'done',
      },
    ],
  },
};

export const AgentThinking: React.FC<AgentThinkingProps> = ({ activeDrug }) => {
  const [expanded, setExpanded] = useState(false);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);

  const scenario = THOUGHT_SCENARIOS[activeDrug] || THOUGHT_SCENARIOS['Nintedanib'];

  // Animate through steps when active drug changes
  useEffect(() => {
    setCurrentStepIdx(0);
    const interval = setInterval(() => {
      setCurrentStepIdx((prev) => {
        if (prev < scenario.steps.length - 1) return prev + 1;
        return prev;
      });
    }, 600);
    return () => clearInterval(interval);
  }, [activeDrug, scenario.steps.length]);

  const activeStep = scenario.steps[currentStepIdx] || scenario.steps[scenario.steps.length - 1];

  return (
    <div className="bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-xl shadow-xs overflow-hidden transition-all text-xs">
      {/* Top Banner Bar */}
      <div className="px-4 py-2.5 flex items-center justify-between gap-3 bg-gradient-to-r from-blue-50/70 via-indigo-50/40 to-white">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-6 h-6 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-2xs">
            <Bot size={14} className="animate-pulse" />
          </div>
          <div className="flex items-center gap-2 min-w-0">
            <span className="font-semibold text-slate-900 tracking-tight shrink-0">
              Agent Thought Stream:
            </span>
            <span className="text-slate-600 truncate font-medium">
              {activeStep.step} — {activeStep.detail}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="hidden md:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
            Neo4j Grounded
          </span>

          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 rounded text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition"
            title={expanded ? 'Collapse thought stream' : 'Expand full reasoning trail'}
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {/* Expanded Step-by-Step Reasoning Trail */}
      {expanded && (
        <div className="p-4 border-t border-slate-100 space-y-2.5 bg-slate-50/60 animate-in fade-in duration-150">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
            Reasoning Chain: {scenario.title}
          </div>
          <div className="space-y-2">
            {scenario.steps.map((st, i) => (
              <div
                key={i}
                className={`p-2.5 rounded-lg border flex items-start gap-2.5 transition ${
                  st.status === 'warning'
                    ? 'bg-rose-50/80 border-rose-200 text-rose-900'
                    : i <= currentStepIdx
                    ? 'bg-white border-slate-200 text-slate-800 shadow-2xs'
                    : 'bg-slate-100/50 border-slate-200/50 text-slate-400'
                }`}
              >
                {st.status === 'warning' ? (
                  <AlertTriangle size={14} className="text-rose-600 shrink-0 mt-0.5" />
                ) : (
                  <CheckCircle2
                    size={14}
                    className={`shrink-0 mt-0.5 ${i <= currentStepIdx ? 'text-blue-600' : 'text-slate-300'}`}
                  />
                )}
                <div className="leading-relaxed">
                  <span className="font-semibold">{st.step}: </span>
                  <span>{st.detail}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
