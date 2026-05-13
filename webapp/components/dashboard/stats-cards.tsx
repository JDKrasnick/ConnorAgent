import { Card, CardContent } from "@/components/ui/card";
import { Building2, SearchCheck, Mail, TrendingUp } from "lucide-react";
import type { PipelineStats } from "@/lib/types";

interface StatCardProps {
  label: string;
  value: number | string;
  icon: React.ElementType;
  description: string;
  highlight?: boolean;
}

function StatCard({ label, value, icon: Icon, description, highlight }: StatCardProps) {
  return (
    <Card className={highlight ? "border-primary/30 bg-primary/5" : undefined}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              {label}
            </p>
            <p className={`mt-1.5 text-2xl font-semibold tabular-nums ${highlight ? "text-primary" : ""}`}>
              {typeof value === "number" ? value.toLocaleString() : value}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">{description}</p>
          </div>
          <div className={`flex h-9 w-9 items-center justify-center rounded-md ${highlight ? "bg-primary/15" : "bg-muted"}`}>
            <Icon className={`h-4 w-4 ${highlight ? "text-primary" : "text-muted-foreground"}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function StatsCards({ stats }: { stats: PipelineStats }) {
  const replyRate = "40%"; // TODO: compute from outreach records
  const cards: StatCardProps[] = [
    {
      label: "Organizations",
      value: stats.cleanedDomains,
      icon: Building2,
      description: "Vetted and in the pipeline",
    },
    {
      label: "Researched",
      value: stats.crawlJobs,
      icon: SearchCheck,
      description: "Websites reviewed",
    },
    {
      label: "Emails Found",
      value: stats.extractedContacts,
      icon: Mail,
      description: "Ready for outreach",
      highlight: true,
    },
    {
      label: "Reply Rate",
      value: replyRate,
      icon: TrendingUp,
      description: "Across all sent emails",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((card) => (
        <StatCard key={card.label} {...card} />
      ))}
    </div>
  );
}
