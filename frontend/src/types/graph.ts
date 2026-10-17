export interface GraphNode {
  id: string;
  label: string;
  type: string;
  color: string;
  size: number;
  properties: Record<string, any>;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface GraphLink {
  id: string;
  source: string;
  target: string;
  type: string;
  label: string;
  properties?: Record<string, any>;
}

export interface SubgraphResponse {
  nodes: GraphNode[];
  links: GraphLink[];
  metrics: {
    node_count: number;
    link_count: number;
    focused_drug: string;
  };
}

export interface EvidenceItem {
  id: string;
  tier: number;
  type: string;
  direction: string;
  summary: string;
  limitations: string;
  source: string;
}

export interface CandidateDrug {
  drug_id: string;
  drug_name: string;
  chembl_id: string;
  mechanism: string;
  approval_status: string;
  targets: string[];
  side_effects: string[];
  evidence_list: EvidenceItem[];
  supporting_evidence_count: number;
  negative_evidence_count: number;
  best_tier: number;
}

export interface KeywordBenchmark {
  disease: string;
  scenario_1: {
    title: string;
    keyword_search: {
      query: string;
      direct_results: number;
      limitation: string;
    };
    graph_retrieval: {
      query: string;
      multi_hop_found: boolean;
      hops: number;
      chain: string[];
      outcome: string;
    };
  };
  scenario_2: {
    title: string;
    keyword_search: {
      query: string;
      direct_results: number;
      limitation: string;
    };
    graph_retrieval: {
      query: string;
      multi_hop_found: boolean;
      evidence_stratification: {
        preclinical: {
          tier: number;
          direction: string;
          summary: string;
        };
        clinical_trial: {
          tier: number;
          direction: string;
          summary: string;
        };
      };
      outcome: string;
    };
  };
}

export interface ResearchPaperItem {
  id: string;
  pmid: string;
  doi: string;
  title: string;
  journal: string;
  pub_date: string;
  abstract: string;
  drug_name: string;
  target_gene?: string;
  evidence_tier?: number;
  evidence_direction?: string;
}

export interface AgentInvestigation {
  question: string;
  matched_entity: string | null;
  answer: string;
  classification: 'supported' | 'warning' | 'insufficient';
  retrieval: {
    multi_hop_paths: number;
    supporting_records?: number;
    negative_records?: number;
    clinical_trials?: string[];
    pubmed_ids?: string[];
    matched_entities?: string[];
  };
  caveat: string;
}

export interface ResearchMemory {
  session_id: string;
  messages: { role: string; content: string; created_at: string }[];
  entities: { name: string; type: string }[];
  reasoning_traces: number;
}

export interface PaperSummary {
  answer: string;
  session_id: string;
  supporting_records: number;
  negative_records: number;
  synthesis_mode: 'groq_grounded' | 'extractive_fallback';
}

