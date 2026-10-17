import { useEffect, useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { AgentInvestigation, PaperSummary, ResearchMemory } from './types/graph';
import {
  ArrowUp,
  BookOpen,
  Bot,
  BrainCircuit,
  CircleHelp,
  FileText,
  FlaskConical,
  History,
  Home,
  LoaderCircle,
  MessageSquare,
  Network,
  Search,
  Sparkles,
  TriangleAlert,
  User,
} from 'lucide-react';

const SESSION_ID = 'demo-researcher';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  drug?: string;
  classification?: string;
  retrieval?: {
    multi_hop_paths?: number;
    clinical_trials?: string[];
    pubmed_ids?: string[];
    supporting_records?: number;
    negative_records?: number;
  };
  timestamp: string;
}

const scenarios = [
  { label: 'Nintedanib evidence', question: 'Summarize the Nintedanib evidence for IPF', drug: 'Nintedanib', icon: Search },
  { label: 'Why Imatinib failed', question: 'Why did Imatinib fail in human IPF trials?', drug: 'Imatinib', icon: TriangleAlert },
  { label: 'Compare mechanisms', question: 'Compare Pirfenidone and Nintedanib mechanisms in IPF', drug: 'Pirfenidone', icon: Network },
  { label: 'Research memory', question: 'What research context has this session stored?', drug: 'Nintedanib', icon: History },
];

export function App() {
  const [question, setQuestion] = useState('');
  const [activeDrug, setActiveDrug] = useState('Nintedanib');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [memory, setMemory] = useState<ResearchMemory | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const fetchMemory = async () => {
    try {
      const response = await fetch(`/api/agent/memory?session_id=${SESSION_ID}`);
      if (response.ok) setMemory(await response.json());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchMemory();
  }, []);

  const inferDrug = (text: string) =>
    ['Nintedanib', 'Imatinib', 'Pirfenidone', 'Pamrevlumab', 'Treprostinil'].find((name) =>
      text.toLowerCase().includes(name.toLowerCase())
    ) || activeDrug;

  const ask = async (forcedQuestion?: string, forcedDrug?: string) => {
    const prompt = (forcedQuestion || question).trim();
    if (!prompt || loading) return;

    const drug = forcedDrug || inferDrug(prompt);
    setActiveDrug(drug);
    setQuestion(''); // Clear input box immediately for good UX

    // 1. Add user message
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: prompt,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const parameters = new URLSearchParams({
        question: prompt,
        drug_name: drug,
        session_id: SESSION_ID,
      });
      const response = await fetch(`/api/agent/investigate?${parameters}`);
      if (response.ok) {
        const data: AgentInvestigation = await response.json();
        const assistantMsg: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: data.answer,
          drug: data.matched_entity || drug,
          classification: data.classification,
          retrieval: data.retrieval,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } else {
        const errorMsg: ChatMessage = {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: 'Failed to communicate with MedTrail backend. Please ensure the server is online.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
      await fetchMemory();
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Error during graph investigation: ${err?.message || 'Network error'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const summarize = async () => {
    const prompt = question.trim() || `Summarize the connected ${activeDrug} research papers for IPF`;
    setQuestion('');
    setLoading(true);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: `✨ ${prompt}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const parameters = new URLSearchParams({
        question: prompt,
        drug_name: activeDrug,
        session_id: SESSION_ID,
      });
      const response = await fetch(`/api/agent/summarize-papers?${parameters}`);
      if (response.ok) {
        const data: PaperSummary = await response.json();
        const assistantMsg: ChatMessage = {
          id: `summary-${Date.now()}`,
          role: 'assistant',
          content: data.answer,
          drug: activeDrug,
          classification: 'supported',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
      await fetchMemory();
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fcfcfd] text-slate-900 flex font-sans">
      {/* Sidebar Navigation */}
      <aside className="hidden md:flex fixed inset-y-0 left-0 w-[68px] bg-white border-r border-slate-200 flex-col items-center py-3 z-20 shadow-2xs">
        <button
          onClick={() => setMessages([])}
          title="New Investigation Chat"
          className="h-10 w-10 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 grid place-items-center shadow-xs transition"
        >
          <span className="text-2xl font-light leading-none">+</span>
        </button>
        <div className="mt-6 flex flex-col gap-2 text-slate-500">
          {[Home, Search, BookOpen, MessageSquare, FileText, Network, BrainCircuit].map(
            (Icon, index) => (
              <button
                key={index}
                className={`h-10 w-10 grid place-items-center rounded-xl transition ${
                  index === 0 ? 'bg-blue-50 text-blue-700' : 'hover:bg-slate-100 hover:text-slate-800'
                }`}
              >
                <Icon size={18} />
              </button>
            )
          )}
        </div>
        <div className="mt-auto flex flex-col gap-3 items-center text-slate-400">
          <CircleHelp size={18} />
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 text-white text-xs font-bold grid place-items-center">
            MT
          </div>
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="flex-1 md:ml-[68px] min-h-screen flex flex-col">
        {/* Top Header */}
        <header className="h-16 flex items-center justify-between px-5 sm:px-8 border-b border-slate-100 bg-white/80 backdrop-blur sticky top-0 z-10">
          <div className="flex items-center gap-2.5 font-semibold text-slate-800">
            <div className="relative h-7 w-7">
              <span className="absolute inset-0 rotate-45 rounded-sm bg-cyan-400" />
              <span className="absolute inset-[6px] rotate-45 rounded-sm bg-blue-600" />
            </div>
            <span>MedTrail</span>
            <span className="text-xs font-normal text-slate-400 hidden sm:inline">
              Research Intelligence
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="inline-flex items-center gap-1.5 bg-emerald-50 text-emerald-700 border border-emerald-100 px-2.5 py-1 rounded-full">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Neo4j Aura Live (79 Nodes • 159 Edges)
            </span>
            <span className="hidden sm:inline-flex items-center gap-1 bg-violet-50 text-violet-700 border border-violet-100 px-2.5 py-1 rounded-full font-medium">
              <Sparkles size={12} /> Groq LLM Active
            </span>
            {memory && (
              <span className="hidden md:inline-flex items-center gap-1 bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full text-xs">
                {memory.messages.length} memory turns
              </span>
            )}
          </div>
        </header>

        {/* Conversation Stream */}
        <div className="flex-1 max-w-[920px] w-full mx-auto px-4 sm:px-6 py-8 space-y-6">
          {messages.length === 0 ? (
            /* Empty State Hero */
            <div className="text-center py-10 sm:py-14 space-y-4">
              <div className="inline-flex items-center gap-2 text-sm text-slate-600 bg-slate-100/80 px-3 py-1 rounded-full">
                <FlaskConical size={16} className="text-cyan-600" /> IPF Research Dossier
              </div>
              <h1 className="text-3xl sm:text-5xl font-semibold tracking-tight text-slate-950">
                What would you like to learn
                <br className="hidden sm:block" /> from the IPF evidence?
              </h1>
              <p className="max-w-2xl mx-auto text-sm sm:text-base text-slate-500 leading-relaxed">
                Explore a deeply curated disease graph: mechanisms, clinical trials, conflicting
                findings, and source-bounded AI paper synthesis with Groq &amp; Neo4j.
              </p>
            </div>
          ) : (
            /* Active Message History */
            <div className="space-y-5">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 sm:gap-4 ${
                    msg.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {msg.role === 'assistant' && (
                    <div
                      className={`h-8 w-8 rounded-xl grid place-items-center shrink-0 mt-0.5 ${
                        msg.classification === 'warning'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-blue-600 text-white'
                      }`}
                    >
                      {msg.classification === 'warning' ? <TriangleAlert size={16} /> : <Bot size={16} />}
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl p-4 sm:p-5 text-sm leading-relaxed shadow-2xs ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-tr-xs'
                        : msg.classification === 'warning'
                        ? 'bg-amber-50/70 border border-amber-200 text-slate-800 rounded-tl-xs'
                        : 'bg-white border border-slate-200 text-slate-800 rounded-tl-xs'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-4 mb-2">
                      <span className="font-semibold text-xs tracking-tight">
                        {msg.role === 'user' ? 'Researcher' : 'MedTrail Agent (Neo4j + Groq)'}
                      </span>
                      <span className="text-[10px] opacity-70">{msg.timestamp}</span>
                    </div>

                    <div className="prose prose-slate max-w-none text-[13.5px] leading-relaxed [&>h2]:text-base [&>h2]:font-bold [&>h2]:text-slate-900 [&>h2]:mt-2 [&>h2]:mb-1 [&>h3]:text-sm [&>h3]:font-bold [&>h3]:text-slate-900 [&>h3]:mt-2 [&>h3]:mb-1 [&>ul]:list-disc [&>ul]:pl-5 [&>ul]:my-2 [&>ul]:space-y-1 [&>ol]:list-decimal [&>ol]:pl-5 [&>ol]:my-2 [&>ol]:space-y-1 [&>p]:my-1.5 [&>table]:border-collapse [&>table]:border [&>table]:border-slate-300 [&>table]:w-full [&>table]:my-3 [&>table_th]:border [&>table_th]:border-slate-300 [&>table_th]:bg-slate-100 [&>table_th]:p-2 [&>table_th]:text-left [&>table_th]:font-semibold [&>table_td]:border [&>table_td]:border-slate-300 [&>table_td]:p-2">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>

                    {/* Metadata / Provenance Badges for Assistant */}
                    {msg.retrieval && (
                      <div className="mt-3.5 pt-3 border-t border-slate-100 flex flex-wrap gap-1.5 text-[11px] text-slate-600">
                        {msg.retrieval.multi_hop_paths ? (
                          <span className="px-2 py-0.5 rounded-md bg-slate-100 font-medium">
                            ⚡ {msg.retrieval.multi_hop_paths} multi-hop paths
                          </span>
                        ) : null}
                        {msg.retrieval.clinical_trials?.map((trial) => (
                          <span
                            key={trial}
                            className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200 font-mono font-medium"
                          >
                            Trial: {trial}
                          </span>
                        ))}
                        {msg.retrieval.pubmed_ids?.slice(0, 3).map((pmid) => (
                          <a
                            key={pmid}
                            href={`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200 hover:underline font-mono"
                          >
                            PMID:{pmid}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="h-8 w-8 rounded-xl bg-slate-200 text-slate-700 grid place-items-center shrink-0 mt-0.5">
                      <User size={16} />
                    </div>
                  )}
                </div>
              ))}

              {/* Live Loading Pulse */}
              {loading && (
                <div className="flex gap-3 items-center text-xs text-slate-500 pl-1">
                  <div className="h-8 w-8 rounded-xl bg-blue-50 text-blue-600 grid place-items-center shrink-0">
                    <LoaderCircle size={16} className="animate-spin" />
                  </div>
                  <span className="animate-pulse font-medium">
                    Traversing Neo4j knowledge graph &amp; synthesizing answer with Groq LLM...
                  </span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Quick Scenario Buttons */}
          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {scenarios.map(({ label, question: scenarioQuestion, drug, icon: Icon }) => (
              <button
                key={label}
                onClick={() => ask(scenarioQuestion, drug)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-medium text-slate-700 hover:border-blue-400 hover:text-blue-700 hover:shadow-xs transition"
              >
                <Icon size={14} className="text-slate-400" />
                {label}
              </button>
            ))}
          </div>

          {/* Chat Input Container */}
          <div className="bg-white rounded-[22px] border border-slate-200 shadow-[0_12px_40px_-15px_rgba(15,23,42,.18)] text-left overflow-hidden sticky bottom-4 z-20">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  ask();
                }
              }}
              placeholder="Ask about Nintedanib, Imatinib, Pirfenidone, or a research finding... (Press Enter to send)"
              className="w-full h-24 resize-none outline-none p-4 text-[14px] placeholder:text-slate-400"
            />
            <div className="border-t border-slate-100 px-3 py-2 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setQuestion('')}
                  title="Clear prompt"
                  className="h-8 w-8 grid place-items-center rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-500 text-sm"
                >
                  ✕
                </button>
                <span className="text-[11px] text-slate-400 hidden sm:inline">
                  Press <strong>Enter</strong> to send, <strong>Shift+Enter</strong> for newline
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={summarize}
                  disabled={loading}
                  className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 hover:bg-violet-50 text-violet-700 border border-violet-200 rounded-lg transition"
                >
                  <Sparkles size={14} /> Summarize papers
                </button>
                <button
                  type="button"
                  onClick={() => ask()}
                  disabled={loading || !question.trim()}
                  className="h-8 w-8 grid place-items-center rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:bg-slate-200 disabled:text-slate-400 transition shadow-xs"
                >
                  {loading ? (
                    <LoaderCircle size={15} className="animate-spin" />
                  ) : (
                    <ArrowUp size={16} />
                  )}
                </button>
              </div>
            </div>
          </div>

          <p className="text-[11px] text-slate-400 text-center pb-2">
            Demo scope: high-depth IPF dossier grounded in Neo4j AuraDB &amp; Groq (llama/gpt-oss).
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
