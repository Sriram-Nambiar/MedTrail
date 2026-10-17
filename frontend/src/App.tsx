import { useState, useEffect } from 'react';
import { EvidenceChain } from './components/EvidenceChain';
import { CandidateCard } from './components/CandidateCard';
import { AgentThinking } from './components/AgentThinking';
import { BenchmarkModal } from './components/BenchmarkModal';
import type { CandidateDrug, KeywordBenchmark } from './types/graph';
import {
  Search,
  Sparkles,
  Database,
  ArrowRight,
  ShieldCheck,
  Layers,
} from 'lucide-react';

export function App() {
  const [diseaseInput, setDiseaseInput] = useState('Idiopathic Pulmonary Fibrosis');
  const [activeDrug, setActiveDrug] = useState<string>('Nintedanib');
  const [candidates, setCandidates] = useState<CandidateDrug[]>([]);
  const [benchmarkData, setBenchmarkData] = useState<KeywordBenchmark | null>(null);
  const [showBenchmark, setShowBenchmark] = useState(false);

  // Fetch Candidates list
  const fetchCandidates = async () => {
    try {
      const res = await fetch('/api/graph/candidates?disease_id=DIS:IPF');
      if (res.ok) {
        const data = await res.json();
        setCandidates(data.candidates || []);
      }
    } catch (err) {
      console.error('Failed to fetch candidates:', err);
    }
  };

  // Fetch Benchmark comparison
  const fetchBenchmark = async () => {
    try {
      const res = await fetch('/api/graph/comparison');
      if (res.ok) {
        const data = await res.json();
        setBenchmarkData(data);
      }
    } catch (err) {
      console.error('Failed to fetch benchmark:', err);
    }
  };

  useEffect(() => {
    fetchCandidates();
    fetchBenchmark();
  }, []);

  const handleInvestigate = (drugName: string, diseaseQuery?: string) => {
    if (diseaseQuery) {
      setDiseaseInput(diseaseQuery);
    }
    setActiveDrug(drugName);
  };

  const selectedCandidate =
    candidates.find((c) => c.drug_name.toLowerCase() === activeDrug.toLowerCase()) ||
    candidates[0];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans flex flex-col">
      {/* 1. Slim, Minimalist Header */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-30 shadow-2xs">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold shadow-xs">
              <Layers size={18} />
            </div>
            <div>
              <span className="font-bold text-slate-900 text-base tracking-tight">MedTrail</span>
              <span className="text-xs text-slate-400 ml-2 hidden sm:inline">
                Graph-Powered Research Discovery
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-600 bg-slate-100 px-2.5 py-1 rounded-full border border-slate-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <Database size={12} className="text-slate-400" />
              <span>Neo4j Aura Live</span>
              <span className="text-slate-400">•</span>
              <span className="text-slate-500 font-medium">61 Curated Entities</span>
            </div>

            <button
              onClick={() => setShowBenchmark(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition"
            >
              <Sparkles size={13} />
              <span>Graph vs Keyword Search</span>
            </button>
          </div>
        </div>
      </header>

      {/* 2. Main Investigation Container */}
      <main className="max-w-5xl mx-auto px-4 py-8 flex-1 w-full space-y-6">
        {/* Disease Investigation Bar */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              Investigate Disease Relationships & Evidence
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Ask MedTrail to traverse the knowledge graph, uncover indirect multi-hop pathways, and evaluate candidate medicines with transparent evidence tiers.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <Search
                size={16}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
              />
              <input
                type="text"
                value={diseaseInput}
                onChange={(e) => setDiseaseInput(e.target.value)}
                placeholder="Enter disease to investigate..."
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
              />
            </div>
            <button
              onClick={() => handleInvestigate('Nintedanib')}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-xs transition flex items-center gap-1.5"
            >
              <span>Investigate</span>
              <ArrowRight size={14} />
            </button>
          </div>

          {/* Quick Investigation Presets */}
          <div className="flex items-center gap-2 flex-wrap pt-1 text-xs">
            <span className="text-slate-400 font-medium">Sample Investigations:</span>
            <button
              onClick={() => handleInvestigate('Nintedanib', 'Idiopathic Pulmonary Fibrosis')}
              className={`px-3 py-1 rounded-full font-medium transition ${
                activeDrug === 'Nintedanib'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              🌟 How Nintedanib was Discovered (Known-Path Validation)
            </button>
            <button
              onClick={() => handleInvestigate('Imatinib', 'Idiopathic Pulmonary Fibrosis')}
              className={`px-3 py-1 rounded-full font-medium transition ${
                activeDrug === 'Imatinib'
                  ? 'bg-amber-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              ⚠️ Why Imatinib Failed (Preserved Conflicting Evidence)
            </button>
            <button
              onClick={() => handleInvestigate('Pirfenidone', 'Idiopathic Pulmonary Fibrosis')}
              className={`px-3 py-1 rounded-full font-medium transition ${
                activeDrug === 'Pirfenidone'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              🧪 Pirfenidone Mechanism (TGF-β Pathway)
            </button>
          </div>
        </div>

        {/* 3. Live AI Agent Thought Stream */}
        <AgentThinking activeDrug={activeDrug} />

        {/* 4. Multi-Hop Evidence Trail */}
        <EvidenceChain drugName={activeDrug} />

        {/* 5. Candidate Investigation Results */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Candidate Medicines & Evidence Hierarchy for {diseaseInput}
            </h2>
            <span className="text-xs text-slate-500">
              Ordered by highest evidence tier first
            </span>
          </div>

          {/* Detailed view of currently focused candidate */}
          {selectedCandidate && (
            <CandidateCard
              candidate={selectedCandidate}
              isSelected={true}
              onSelect={() => {}}
            />
          )}

          {/* Quick list of other candidates to inspect */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
            {candidates
              .filter((c) => c.drug_name.toLowerCase() !== activeDrug.toLowerCase())
              .map((cand) => (
                <div
                  key={cand.drug_id}
                  onClick={() => handleInvestigate(cand.drug_name)}
                  className="bg-white rounded-xl border border-slate-200 p-4 hover:border-slate-300 hover:shadow-xs transition cursor-pointer flex flex-col justify-between space-y-2 text-xs"
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900 text-sm">{cand.drug_name}</span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        Tier {cand.best_tier}
                      </span>
                    </div>
                    <p className="text-slate-500 text-[11px] line-clamp-2 mt-1">
                      {cand.mechanism}
                    </p>
                  </div>
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-blue-600 font-medium text-[11px]">
                    <span>Inspect Evidence Trail</span>
                    <ArrowRight size={12} />
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* 6. Scientific Disclaimer */}
        <div className="bg-slate-100/80 border border-slate-200 rounded-xl p-4 text-xs text-slate-600 space-y-1">
          <div className="font-semibold text-slate-800 flex items-center gap-1.5">
            <ShieldCheck size={14} className="text-blue-600" />
            MedTrail Scientific Limitations & Grounding Guarantee
          </div>
          <p className="leading-relaxed">
            MedTrail is an exploratory hypothesis-generation tool. Indirect graph paths indicate biological connections worth investigating, but do not establish clinical efficacy or safety. All conclusions preserve negative findings and provide direct citations to ClinicalTrials.gov and PubMed records.
          </p>
        </div>
      </main>

      {/* 7. Benchmark Modal */}
      {showBenchmark && (
        <BenchmarkModal
          data={benchmarkData}
          onClose={() => setShowBenchmark(false)}
        />
      )}
    </div>
  );
}

export default App;
