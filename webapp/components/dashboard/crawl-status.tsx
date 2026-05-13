"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import type { CrawlJobStatus } from "@/lib/types";

const STATUS_CONFIG = [
  { key: "completed", label: "Completed", color: "#22c55e" },
  { key: "pending", label: "Pending", color: "#f59e0b" },
  { key: "failed", label: "Failed", color: "#ef4444" },
] as const;

interface TooltipPayload {
  name: string;
  value: number;
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-sm shadow-md">
      <p className="font-medium">{payload[0].name}</p>
      <p className="text-muted-foreground">{payload[0].value.toLocaleString()} jobs</p>
    </div>
  );
}

export function CrawlStatusCard({ status }: { status: CrawlJobStatus }) {
  const total = status.completed + status.pending + status.failed;
  const data = STATUS_CONFIG.map(({ key, label, color }) => ({
    name: label,
    value: status[key],
    color,
  }));

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">Crawl Job Status</CardTitle>
        <p className="text-xs text-muted-foreground">{total.toLocaleString()} total jobs</p>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <ResponsiveContainer width={100} height={100}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={28}
                outerRadius={44}
                dataKey="value"
                strokeWidth={0}
              >
                {data.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-col gap-2">
            {data.map((entry) => (
              <div key={entry.name} className="flex items-center gap-2">
                <div
                  className="h-2 w-2 rounded-full shrink-0"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-xs text-muted-foreground">{entry.name}</span>
                <Badge variant="secondary" className="ml-auto text-xs tabular-nums">
                  {entry.value}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
