"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import type { PipelineStats } from "@/lib/types";

const STAGES = [
  { key: "cleanedDomains", label: "Organizations", color: "#818cf8" },
  { key: "crawlJobs", label: "Researched", color: "#6366f1" },
  { key: "extractedContacts", label: "Emails Found", color: "#4f46e5" },
] as const;

interface TooltipPayload {
  value: number;
  name: string;
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-sm shadow-md">
      <p className="font-medium">{label}</p>
      <p className="text-muted-foreground">{payload[0].value.toLocaleString()}</p>
    </div>
  );
}

export function PipelineFunnel({ stats }: { stats: PipelineStats }) {
  const data = STAGES.map(({ key, label, color }) => ({
    label,
    value: stats[key],
    color,
  }));

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">Pipeline Overview</CardTitle>
        <p className="text-xs text-muted-foreground">
          How many organizations have been found, researched, and turned into emails
        </p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={data} layout="vertical" margin={{ left: 16, right: 48, top: 4, bottom: 4 }}>
            <XAxis
              type="number"
              tick={{ fontSize: 11, fill: "currentColor", opacity: 0.5 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) =>
                v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v)
              }
            />
            <YAxis
              type="category"
              dataKey="label"
              tick={{ fontSize: 12, fill: "currentColor" }}
              tickLine={false}
              axisLine={false}
              width={90}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "transparent" }} />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={26}>
              {data.map((entry) => (
                <Cell key={entry.label} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
