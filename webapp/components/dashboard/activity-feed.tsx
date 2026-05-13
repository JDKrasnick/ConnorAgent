import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, ClipboardCheck, Mail, AlertTriangle } from "lucide-react";
import { CATEGORY_LABELS, CATEGORY_COLORS, type ActivityEvent } from "@/lib/types";

const TYPE_CONFIG = {
  collect: { icon: Search, color: "text-blue-500" },
  clean: { icon: ClipboardCheck, color: "text-violet-500" },
  crawl: { icon: ClipboardCheck, color: "text-indigo-500" },
  extract: { icon: Mail, color: "text-emerald-500" },
  outreach: { icon: Mail, color: "text-amber-500" },
};

function formatRelative(iso: string) {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function isWarning(msg: string) {
  return msg.toLowerCase().includes("could not") || msg.toLowerCase().includes("retry");
}

export function ActivityFeed({ events }: { events: ActivityEvent[] }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">Recent Activity</CardTitle>
        <p className="text-xs text-muted-foreground">What the system has been doing</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {events.map((event) => {
            const config = TYPE_CONFIG[event.type];
            const warn = isWarning(event.message);
            const Icon = warn ? AlertTriangle : config.icon;
            const iconColor = warn ? "text-amber-500" : config.color;

            return (
              <div key={event.id} className="flex items-start gap-3">
                <div className={`mt-0.5 ${iconColor}`}>
                  <Icon className="h-3.5 w-3.5 shrink-0" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs leading-snug text-foreground/90">
                    {event.message}
                  </p>
                  <div className="mt-1 flex items-center gap-2">
                    {event.category && (
                      <Badge
                        variant="secondary"
                        className={`h-4 px-1.5 text-[10px] font-medium ${CATEGORY_COLORS[event.category]}`}
                      >
                        {CATEGORY_LABELS[event.category]}
                      </Badge>
                    )}
                    <span className="text-[11px] text-muted-foreground">
                      {formatRelative(event.timestamp)}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
