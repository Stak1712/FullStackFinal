import { http } from "./http";

export type ExternalResource = {
  title: string;
  description?: string | null;
  url: string;
  source: string;
  stars: number;
  language?: string | null;
  updated_at?: string | null;
};

export type ExternalResourceResponse = {
  query: string;
  source: string;
  external_status: "live" | "fallback" | string;
  items: ExternalResource[];
  warning?: string | null;
};

export async function fetchInterviewPrepResources(skill: string, limit = 6) {
  const response = await http.get<ExternalResourceResponse>("/resources/interview-prep", {
    params: { skill, limit },
  });
  return response.data;
}
