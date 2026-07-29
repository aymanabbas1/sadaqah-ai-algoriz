import type { Ngo, RegionStat, SourceRecord } from "./types";

export type GlobePayload = {
  regions: RegionStat[];
  summary: {
    crisisProfiles: number;
    countriesCovered: number;
    sourceRecords: number;
  };
};

export type ChatPayload = {
  message: string;
  contextType: "crisis" | "ngo_comparison";
  crisisId?: string;
  ngoIds?: string[];
  conversation?: Array<{ role: "user" | "assistant"; content: string }>;
};

export type ChatResponse = {
  message: string;
  intent: string;
  mode: "groq" | "deterministic";
  sources: SourceRecord[];
};

const request = async <T>(path: string, options?: RequestInit): Promise<T> => {
  const response = await fetch(`/api/v1${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!response.ok) throw new Error(`API request failed with ${response.status}`);
  return response.json() as Promise<T>;
};

export const api = {
  globe: () => request<GlobePayload>("/globe"),
  crisis: (crisisId: string) => request<RegionStat>(`/crises/${crisisId}`),
  ngos: () => request<Ngo[]>("/ngos"),
  crisisNgos: (crisisId: string) => request<Ngo[]>(`/crises/${crisisId}/ngos`),
  compare: (ids: string[], crisisId: string) => request<{ organizations: Ngo[]; rationale: string }>("/ngos/compare", {
    method: "POST",
    body: JSON.stringify({ ids, crisisId }),
  }),
  chat: (payload: ChatPayload) => request<ChatResponse>("/chat", { method: "POST", body: JSON.stringify(payload) }),
};
