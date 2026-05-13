"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CATEGORY_LABELS, CATEGORY_COLORS, type CategoryBreakdown } from "@/lib/types";

function ProgressBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{ width: `${pct}%`, backgroundColor: color }}
      />
    </div>
  );
}

const ROW_COLORS: Record<string, string> = {
  college_art: "#7c3aed",
  college_chinese: "#e11d48",
  golf_clubs: "#059669",
  hs_art: "#d97706",
};

export function CategoryBreakdownCard({ data }: { data: CategoryBreakdown[] }) {
  const maxContacts = Math.max(...data.map((d) => d.contacts));

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">By Category</CardTitle>
        <p className="text-xs text-muted-foreground">
          Emails found per target group
        </p>
      </CardHeader>
      <CardContent className="space-y-5">
        {data.map((row) => (
          <div key={row.category} className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Badge
                variant="secondary"
                className={`text-xs font-medium ${CATEGORY_COLORS[row.category]}`}
              >
                {CATEGORY_LABELS[row.category]}
              </Badge>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span>{row.cleanedRelevant.toLocaleString()} orgs</span>
                <span className="font-semibold text-foreground tabular-nums">
                  {row.contacts.toLocaleString()} emails
                </span>
              </div>
            </div>
            <ProgressBar
              value={row.contacts}
              max={maxContacts}
              color={ROW_COLORS[row.category]}
            />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
