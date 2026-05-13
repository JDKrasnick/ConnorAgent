export type Category = "college_art" | "college_chinese" | "golf_clubs" | "hs_art";

export const CATEGORY_LABELS: Record<Category, string> = {
  college_art: "College Art",
  college_chinese: "College Chinese",
  golf_clubs: "Golf Clubs",
  hs_art: "HS Art",
};

export const CATEGORY_COLORS: Record<Category, string> = {
  college_art: "bg-violet-100 text-violet-800",
  college_chinese: "bg-rose-100 text-rose-800",
  golf_clubs: "bg-emerald-100 text-emerald-800",
  hs_art: "bg-amber-100 text-amber-800",
};

export interface PipelineStats {
  rawResults: number;
  domains: number;
  cleanedDomains: number;
  crawlJobs: number;
  extractedContacts: number;
}

export interface CategoryBreakdown {
  category: Category;
  rawResults: number;
  domains: number;
  cleanedRelevant: number;
  crawled: number;
  contacts: number;
}

export interface CrawlJobStatus {
  pending: number;
  completed: number;
  failed: number;
}

export interface ActivityEvent {
  id: string;
  type: "collect" | "clean" | "crawl" | "extract" | "outreach";
  message: string;
  timestamp: string;
  category?: Category;
}

export interface Contact {
  id: string;
  domain: string;
  category: Category;
  email: string;
  name: string | null;
  title: string | null;
  role_type: string | null;
  is_targeted: boolean;
  confidence: number | null;
  page_url: string | null;
  extracted_at: string;
  // from extracted_metadata
  org_name: string | null;
  org_description: string | null;
  sales_notes: string | null;
  contact_summary: string | null;
}

export interface OutreachRecord {
  id: string;
  contact: Contact;
  status: "pending" | "sent" | "replied" | "bounced";
  subject: string | null;
  sent_at: string | null;
  replied_at: string | null;
}

export interface PipelineStage {
  id: string;
  name: string;
  description: string;
  status: "idle" | "running" | "success" | "error";
  lastRunAt: string | null;
  itemsProcessed: number | null;
}

export interface JobLogEntry {
  id: string;
  stage: string;
  message: string;
  level: "info" | "warn" | "error";
  timestamp: string;
}
