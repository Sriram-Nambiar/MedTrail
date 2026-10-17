import { useState, useEffect } from 'react';
import { GraphCanvas } from './components/GraphCanvas';
import { EntityInspector } from './components/EntityInspector';
import { CandidateTable } from './components/CandidateTable';
import { BenchmarkModal } from './components/BenchmarkModal';
import { AgentThinking } from './components/AgentThinking';
import type { GraphNode, GraphLink, CandidateDrug, KeywordBenchmark, SubgraphResponse } from './types/graph';
import { GitBranch, Table as TableIcon, Sparkles, Database } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'graph' | 'table'>('graph');
  const [selectedDrug, setSelectedDrug] = useState<string>('Nintedanib');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [links, setLinks] = useState<GraphLink[]>([]);
  const [candidates, setCandidates] = useState<CandidateDrug[]>([]);
  const [benchmarkData, setBenchmarkData] = useState<KeywordBenchmark | null>(null);
  const [showBenchmark, setShowBenchmark] = useState(false);
  const [loading, setLoading] = useState(true);

  // Fetch Subgraph for active drug preset
  const fetchSubgraph = async (drugName: string) => {
    try {
      setLoading(true);
      const url = `/api/graph/subgraph?drug_name=${encodeURIComponent(drugName)}`;
      const res = await fetch(url);
      if (res.ok) {
        const data: SubgraphResponse = await res.json();
        setNodes(data.nodes);
        setLinks(data.links);
      }
    } catch (err) {
      console.error('Failed to fetch subgraph:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch Candidates list
  const fetchCandidates = async () => {
    try {
      const res = await fetch('/api/graph/candidates');
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
    fetchSubgraph(selectedDrug);
    fetchCandidates();
    fetchBenchmark();
  }, [selectedDrug]);

  const handleSelectDrug = (drugName: string) => {
    setSelectedDrug(drugName);
    setSelectedNode(null);
    if (activeTab !== 'graph') {
      setActiveTab('graph');
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-50 text-slate-800 font-sans">
      {/* 1. Header (Minimalist & Uncluttered) */}
      <header className="h-14 border-b border-slate-200 bg-white px-5 flex items-center justify-between shrink-0 shadow-2xs z-30">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold shadow-xs">
            <GitBranch size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 text-base tracking-tight">MedTrail</span>
              <span className="text-[11px] font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full border border-slate-200">
                Idiopathic Pulmonary Fibrosis (IPF)
              </span>
            </div>
          </div>
        </div>

        {/* Database Status indicator */}
        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <Database size={13} className="text-slate-400" />
          <span className="font-medium text-slate-700">Neo4j Aura Live</span>
          <span className="text-slate-400">•</span>
          <span className="text-slate-500">61 nodes & 93 edges</span>
        </div>

        {/* View Switchers */}
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
            <button
              onClick={() => setActiveTab('graph')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition ${
                activeTab === 'graph'
                  ? 'bg-white text-slate-900 shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <GitBranch size={14} />
              <span>Graph View</span>
            </button>
            <button
              onClick={() => setActiveTab('table')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition ${
                activeTab === 'table'
                  ? 'bg-white text-slate-900 shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <TableIcon size={14} />
              <span>Candidate Ranking</span>
            </button>
          </div>

          <button
            onClick={() => setShowBenchmark(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition"
          >
            <Sparkles size={13} />
            <span className="hidden md:inline">Graph vs Keyword</span>
          </button>
        </div>
      </header>

      {/* 2. Uncluttered Preset Exploration Strip */}
      <div className="h-11 border-b border-slate-200 bg-white/70 backdrop-blur-xs px-5 flex items-center gap-2 shrink-0 overflow-x-auto text-xs">
        <span className="text-slate-400 font-medium whitespace-nowrap text-[11px] uppercase tracking-wider mr-1">
          Explore Paths:
        </span>

        <button
          onClick={() => handleSelectDrug('Nintedanib')}
          className={`px-3 py-1 rounded-full font-medium transition whitespace-nowrap ${
            selectedDrug === 'Nintedanib'
              ? 'bg-blue-600 text-white shadow-2xs'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          🌟 Rediscover Nintedanib
        </button>

        <button
          onClick={() => handleSelectDrug('Imatinib')}
          className={`px-3 py-1 rounded-full font-medium transition whitespace-nowrap ${
            selectedDrug === 'Imatinib'
              ? 'bg-amber-600 text-white shadow-2xs'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          ⚠️ Imatinib Conflicting Evidence
        </button>

        <button
          onClick={() => handleSelectDrug('Pirfenidone')}
          className={`px-3 py-1 rounded-full font-medium transition whitespace-nowrap ${
            selectedDrug === 'Pirfenidone'
              ? 'bg-blue-600 text-white shadow-2xs'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          🧪 Pirfenidone Mechanism
        </button>

        <button
          onClick={() => handleSelectDrug('Pamrevlumab')}
          className={`px-3 py-1 rounded-full font-medium transition whitespace-nowrap ${
            selectedDrug === 'Pamrevlumab'
              ? 'bg-blue-600 text-white shadow-2xs'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          🔬 Pamrevlumab Phase 3 Result
        </button>

        <button
          onClick={() => handleSelectDrug('all')}
          className={`px-3 py-1 rounded-full font-medium transition whitespace-nowrap ${
            selectedDrug === 'all'
              ? 'bg-slate-800 text-white shadow-2xs'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          🌐 Full IPF Graph
        </button>
      </div>

      {/* 3. Main Workspace Area */}
      <main className="flex-1 relative overflow-hidden p-4 flex flex-col gap-2.5">
        {/* Agent Thought Stream */}
        <AgentThinking activeDrug={selectedDrug} />

        {activeTab === 'graph' ? (
          <div className="relative w-full flex-1 min-h-0">
            {loading && (
              <div className="absolute inset-0 bg-white/60 backdrop-blur-2xs flex items-center justify-center z-10 text-xs font-medium text-slate-500">
                Traversing Neo4j Graph...
              </div>
            )}
            <GraphCanvas
              nodes={nodes}
              links={links}
              selectedNode={selectedNode}
              onSelectNode={(node) => setSelectedNode(node)}
            />
            {/* Slide-out Evidence Inspector */}
            <EntityInspector
              node={selectedNode}
              onClose={() => setSelectedNode(null)}
            />
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto max-w-6xl mx-auto w-full">
            <CandidateTable
              candidates={candidates}
              onSelectCandidate={(drug) => handleSelectDrug(drug)}
            />
          </div>
        )}
      </main>

      {/* 4. Benchmark Modal */}
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
