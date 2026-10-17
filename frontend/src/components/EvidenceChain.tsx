import React from 'react';
import { ArrowRight, Activity, Dna, Target, Pill, FileCheck, BookOpen } from 'lucide-react';

interface ChainStep {
  type: string;
  label: string;
  subtitle?: string;
  icon: 'disease' | 'pathway' | 'target' | 'drug' | 'trial' | 'paper';
  color: string;
}

interface EvidenceChainProps {
  drugName: string;
  onSelectNode?: (label: string) => void;
}

export const EvidenceChain: React.FC<EvidenceChainProps> = ({ drugName }) => {
  const getChain = (): ChainStep[] => {
    switch (drugName) {
      case 'Nintedanib':
        return [
          {
            type: 'Disease',
            label: 'Idiopathic Pulmonary Fibrosis',
            subtitle: 'MONDO:0008383',
            icon: 'disease',
            color: 'bg-rose-50 border-rose-200 text-rose-800',
          },
          {
            type: 'Biological Pathway',
            label: 'FGFR & PDGF Signaling',
            subtitle: 'Reactome:R-HSA-190369',
            icon: 'pathway',
            color: 'bg-purple-50 border-purple-200 text-purple-800',
          },
          {
            type: 'Protein Target',
            label: 'FGFR1-3 & PDGFRα/β',
            subtitle: 'Receptor Tyrosine Kinases',
            icon: 'target',
            color: 'bg-sky-50 border-sky-200 text-sky-800',
          },
          {
            type: 'Repurposed Drug',
            label: 'Nintedanib (Ofev)',
            subtitle: 'Triple Angiokinase Inhibitor',
            icon: 'drug',
            color: 'bg-emerald-50 border-emerald-200 text-emerald-800',
          },
          {
            type: 'Clinical Trial',
            label: 'INPULSIS Phase 3',
            subtitle: 'NCT01335464 (1,066 patients)',
            icon: 'trial',
            color: 'bg-amber-50 border-amber-200 text-amber-800',
          },
          {
            type: 'Evidence Outcome',
            label: '50% Slower FVC Loss',
            subtitle: 'Tier 1 • NEJM 2014',
            icon: 'paper',
            color: 'bg-teal-50 border-teal-200 text-teal-800',
          },
        ];
      case 'Imatinib':
        return [
          {
            type: 'Disease',
            label: 'Idiopathic Pulmonary Fibrosis',
            subtitle: 'Progressive lung scarring',
            icon: 'disease',
            color: 'bg-rose-50 border-rose-200 text-rose-800',
          },
          {
            type: 'Biological Pathway',
            label: 'PDGF Receptor Cascade',
            subtitle: 'Fibroblast proliferation drive',
            icon: 'pathway',
            color: 'bg-purple-50 border-purple-200 text-purple-800',
          },
          {
            type: 'Protein Target',
            label: 'PDGFRB & c-KIT',
            subtitle: 'Tyrosine Kinase Receptors',
            icon: 'target',
            color: 'bg-sky-50 border-sky-200 text-sky-800',
          },
          {
            type: 'Investigated Drug',
            label: 'Imatinib (Gleevec)',
            subtitle: 'Oncology TKI',
            icon: 'drug',
            color: 'bg-amber-50 border-amber-200 text-amber-800',
          },
          {
            type: 'Clinical Trial',
            label: 'Phase 2 Trial (119 pts)',
            subtitle: 'NCT00130520 (96 weeks)',
            icon: 'trial',
            color: 'bg-rose-50 border-rose-200 text-rose-800',
          },
          {
            type: 'Evidence Outcome',
            label: 'No Clinical Benefit',
            subtitle: 'Tier 1 • AJRCCM 2010',
            icon: 'paper',
            color: 'bg-rose-50 border-rose-300 text-rose-900',
          },
        ];
      default:
        return [
          {
            type: 'Disease',
            label: 'Idiopathic Pulmonary Fibrosis',
            subtitle: 'MONDO:0008383',
            icon: 'disease',
            color: 'bg-rose-50 border-rose-200 text-rose-800',
          },
          {
            type: 'Biological Pathway',
            label: 'TGF-β Receptor Complex',
            subtitle: 'Collagen synthesis drive',
            icon: 'pathway',
            color: 'bg-purple-50 border-purple-200 text-purple-800',
          },
          {
            type: 'Protein Target',
            label: 'TGFB1 Cytokine',
            subtitle: 'Pro-fibrotic cytokine',
            icon: 'target',
            color: 'bg-sky-50 border-sky-200 text-sky-800',
          },
          {
            type: 'Approved Drug',
            label: 'Pirfenidone (Esbriet)',
            subtitle: 'Antifibrotic agent',
            icon: 'drug',
            color: 'bg-emerald-50 border-emerald-200 text-emerald-800',
          },
          {
            type: 'Clinical Trial',
            label: 'ASCEND Phase 3',
            subtitle: 'NCT01366209',
            icon: 'trial',
            color: 'bg-amber-50 border-amber-200 text-amber-800',
          },
          {
            type: 'Evidence Outcome',
            label: '47.9% Progression Reduction',
            subtitle: 'Tier 1 • NEJM 2014',
            icon: 'paper',
            color: 'bg-teal-50 border-teal-200 text-teal-800',
          },
        ];
    }
  };

  const steps = getChain();

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'disease':
        return <Activity size={14} className="text-rose-600" />;
      case 'pathway':
        return <Dna size={14} className="text-purple-600" />;
      case 'target':
        return <Target size={14} className="text-sky-600" />;
      case 'drug':
        return <Pill size={14} className="text-emerald-600" />;
      case 'trial':
        return <FileCheck size={14} className="text-amber-600" />;
      default:
        return <BookOpen size={14} className="text-teal-600" />;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
          Multi-Hop Evidence Trail (Neo4j Graph Path)
        </h4>
        <span className="text-[11px] text-slate-500">
          5 connected hops across verified databases
        </span>
      </div>

      {/* Horizontal step chain */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center gap-2 overflow-x-auto pb-1">
        {steps.map((st, i) => (
          <React.Fragment key={i}>
            <div
              className={`flex-1 min-w-[140px] p-2.5 rounded-lg border ${st.color} transition hover:shadow-xs`}
            >
              <div className="flex items-center gap-1.5 mb-1">
                {getIcon(st.icon)}
                <span className="text-[10px] font-bold uppercase tracking-wider opacity-75">
                  {st.type}
                </span>
              </div>
              <div className="font-semibold text-xs leading-snug">{st.label}</div>
              {st.subtitle && (
                <div className="text-[10px] opacity-75 mt-0.5">{st.subtitle}</div>
              )}
            </div>

            {i < steps.length - 1 && (
              <div className="hidden md:flex items-center justify-center text-slate-300 shrink-0">
                <ArrowRight size={16} />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
