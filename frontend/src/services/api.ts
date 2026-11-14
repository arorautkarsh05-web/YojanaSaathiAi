const API_BASE = '/api/v1';

export interface FarmerProfileInput {
  district: string;
  landholding_acres?: number | null;
  farmer_category?: string | null;
  primary_crops?: string[];
  social_category?: string | null;
  irrigation_source?: string | null;
  is_temporary?: boolean;
}

export interface RuleOutcome {
  rule_code: string;
  title_en: string;
  title_hi: string;
  status: 'PASS' | 'FAIL' | 'UNKNOWN';
  reason: string;
  citation: string;
  is_mandatory: boolean;
}

export interface SchemeEvaluation {
  scheme_code: string;
  official_name_en: string;
  official_name_hi: string;
  department: string;
  level: string;
  benefit_type: string;
  benefit_summary_en: string;
  benefit_summary_hi: string;
  overall_status: 'LIKELY_ELIGIBLE' | 'NEEDS_MORE_INFO' | 'LIKELY_NOT_ELIGIBLE';
  passed_rules: RuleOutcome[];
  failed_rules: RuleOutcome[];
  unknown_rules: RuleOutcome[];
  official_portal_url: string;
  verified_at: string;
  source_title: string;
  source_section: string;
  source_url: string;
  ranking_score?: number;
  ranking_factors?: {
    need_relevance_pct?: number;
    eligibility_score?: number;
    geo_relevance?: number;
    evidence_freshness?: number;
    matched_needs?: string[];
    weights?: string;
  };
  recommendation_reason?: string;
  readiness_state?: string;
}

export interface ConvergenceGraphNode {
  id: string;
  label_en: string;
  label_hi: string;
  department: string;
  level: string;
}

export interface ConvergenceGraphEdge {
  source: string;
  target: string;
  status: 'COMPATIBLE_CONFIRMED' | 'INCOMPATIBLE_CONFIRMED' | 'UNKNOWN_REQUIRES_VERIFICATION';
  evidence_summary: string;
  source_title: string;
}

export interface UnitAmbiguityNotice {
  field: string;
  issue: string;
  clarification_prompt_hi: string;
  clarification_prompt_en: string;
}

export interface ConversationalIntakeResponse {
  detected_language: string;
  intent: string;
  extracted_parameters: {
    district?: string | null;
    landholding_acres?: number | null;
    landholding_raw?: string | null;
    land_unit?: string | null;
    crops: string[];
    stated_needs: string[];
    irrigation_source?: string | null;
    social_category?: string | null;
  };
  ambiguities: UnitAmbiguityNotice[];
  missing_information: string[];
  follow_up_questions_hi: string[];
  follow_up_questions_en: string[];
  can_proceed_to_evaluation: boolean;
  structured_profile_candidate?: FarmerProfileInput | null;
  summary_message: string;
}

export interface ConvergenceGraphResponse {
  nodes: ConvergenceGraphNode[];
  edges: ConvergenceGraphEdge[];
  updated_at: string;
}

export interface PairwiseConvergence {
  scheme_code_a: string;
  scheme_code_b: string;
  status: 'COMPATIBLE_CONFIRMED' | 'INCOMPATIBLE_CONFIRMED' | 'UNKNOWN_REQUIRES_VERIFICATION';
  evidence_text: string;
  authoritative_source: string;
  source_section: string;
  verified_by: string;
  verified_at: string;
}

export interface ChecklistItem {
  id: string;
  title_en: string;
  title_hi: string;
  required_for_schemes: string[];
  is_ready: boolean;
  source_authority: string;
}

export interface OfficialStep {
  step_number: number;
  title_en: string;
  title_hi: string;
  description_en: string;
  description_hi: string;
  portal_or_destination: string;
  is_independent: boolean;
}

export interface ActionPlanData {
  plan_number: string;
  created_at: string;
  selected_schemes: SchemeEvaluation[];
  convergence_summary: PairwiseConvergence[];
  checklist_items: ChecklistItem[];
  official_steps: OfficialStep[];
  disclaimer: string;
}

// Token helper for authorization headers
let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
  accessToken = token;
};

export const getAccessToken = () => accessToken;

const getHeaders = () => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  return headers;
};

// Safe JSON parser to prevent "Unexpected end of JSON input" errors
async function safeJson(res: Response): Promise<any> {
  let text = '';
  try {
    text = await res.text();
  } catch {
    return { detail: 'सर्वर से उत्तर पढ़ने में विफल (Failed to read server response).' };
  }
  if (!text || text.trim() === '') {
    if (!res.ok) {
      if (res.status === 502 || res.status === 504 || res.status === 500) {
        return { detail: 'बैकएंड सर्वर से संपर्क नहीं हो सका। कृपया सुनिश्चित करें कि बैकएंड पोर्ट 8000 पर चल रहा है (Cannot reach backend on port 8000).' };
      }
      return { detail: `अनुरोध विफल रहा (Status ${res.status})` };
    }
    return {};
  }
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text };
  }
}

export const api = {
  async getSchemes(): Promise<any[]> {
    try {
      const res = await fetch(`${API_BASE}/schemes`, { credentials: 'include' });
      const data = await safeJson(res);
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to fetch schemes catalogue');
      }
      return data;
    } catch (e: any) {
      throw new Error(e.message || 'Network error fetching schemes');
    }
  },

  async getRecommendations(statedNeeds: string[], profile: FarmerProfileInput): Promise<{ schemes: SchemeEvaluation[] }> {
    const res = await fetch(`${API_BASE}/recommendations`, {
      method: 'POST',
      headers: getHeaders(),
      credentials: 'include',
      body: JSON.stringify({ stated_needs: statedNeeds, profile }),
    });
    const data = await safeJson(res);
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to evaluate recommendations');
    }
    return data;
  },

  async checkConvergence(schemeCodes: string[]): Promise<{ pairs: PairwiseConvergence[] }> {
    const res = await fetch(`${API_BASE}/convergence/check`, {
      method: 'POST',
      headers: getHeaders(),
      credentials: 'include',
      body: JSON.stringify({ scheme_codes: schemeCodes }),
    });
    const data = await safeJson(res);
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to evaluate multi-scheme convergence');
    }
    return data;
  },

  async getConvergenceGraph(): Promise<ConvergenceGraphResponse> {
    const res = await fetch(`${API_BASE}/convergence/graph`, {
      headers: getHeaders(),
      credentials: 'include',
    });
    const data = await safeJson(res);
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to fetch convergence graph');
    }
    return data;
  },

  async createActionPlan(
    profile: FarmerProfileInput,
    selectedSchemeCodes: string[],
    checklistStates: Record<string, boolean> = {}
  ): Promise<ActionPlanData> {
    const res = await fetch(`${API_BASE}/action-plans`, {
      method: 'POST',
      headers: getHeaders(),
      credentials: 'include',
      body: JSON.stringify({
        profile,
        selected_scheme_codes: selectedSchemeCodes,
        checklist_states: checklistStates,
      }),
    });
    const data = await safeJson(res);
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to generate action plan');
    }
    return data;
  },

  async queryAssistant(query: string, schemeCode?: string, language?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/assistant/query`, {
      method: 'POST',
      headers: getHeaders(),
      credentials: 'include',
      body: JSON.stringify({ query, scheme_code: schemeCode, language }),
    });
    const data = await safeJson(res);
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to query assistant');
    }
    return data;
  },

  async naturalLanguageIntake(text: string, preferredLanguage: string = 'hi'): Promise<ConversationalIntakeResponse> {
    const res = await fetch(`${API_BASE}/assistant/intake`, {
      method: 'POST',
      headers: getHeaders(),
      credentials: 'include',
      body: JSON.stringify({ text, preferred_language: preferredLanguage }),
    });
    const data = await safeJson(res);
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to process natural language intake');
    }
    return data;
  },

  async register(email: string, password: string, displayName?: string, termsConsented: boolean = true): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, display_name: displayName, terms_consented: termsConsented }),
      });
      const data = await safeJson(res);
      if (!res.ok) {
        throw new Error(data.detail || 'पंजीकरण विफल रहा (Registration failed)');
      }
      return data;
    } catch (e: any) {
      if (e.message && e.message.includes('Failed to fetch')) {
        throw new Error('बैकएंड सर्वर चालू नहीं है। कृपया टर्मिनल में "npm start" चलाएँ (Backend server is offline on port 8000).');
      }
      throw e;
    }
  },

  async login(email: string, password: string): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });
      const data = await safeJson(res);
      if (!res.ok) {
        throw new Error(data.detail || 'लॉगिन विफल रहा (Login failed)');
      }
      setAccessToken(data.access_token);
      return data;
    } catch (e: any) {
      if (e.message && e.message.includes('Failed to fetch')) {
        throw new Error('बैकएंड सर्वर चालू नहीं है। कृपया टर्मिनल में "npm start" चलाएँ (Backend server is offline on port 8000).');
      }
      throw e;
    }
  },

  async getMe(): Promise<any> {
    if (!accessToken) return null;
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: getHeaders(),
        credentials: 'include',
      });
      if (!res.ok) return null;
      return await safeJson(res);
    } catch {
      return null;
    }
  },

  async logout(): Promise<void> {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: getHeaders(),
        credentials: 'include',
      });
    } catch {}
    setAccessToken(null);
  },

  async getAdminOverview(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/overview`, {
      headers: getHeaders(),
      credentials: 'include',
    });
    const data = await safeJson(res);
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to fetch admin overview');
    }
    return data;
  }
};
