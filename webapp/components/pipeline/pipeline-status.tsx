"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Play,
  Loader2,
  CheckCircle,
  AlertCircle,
  Building2,
  Mail,
  Clock,
} from "lucide-react";

type RunStatus = "idle" | "running" | "success" | "error";

interface PipelineStatusProps {
  initialStatus: RunStatus;
  lastRunAt: string | null;
  organizationsFound: number;
  emailsFound: number;
}

function formatTime(iso: string | null) {
  if (!iso) return null;
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

const STATUS_UI: Record<RunStatus, { label: string; labelClass: string; icon: React.ElementType; iconClass: string }> = {
  idle: { label: "Ready to run", labelClass: "text-muted-foreground", icon: Clock, iconClass: "text-muted-foreground" },
  running: { label: "Running…", labelClass: "text-blue-600", icon: Loader2, iconClass: "text-blue-500 animate-spin" },
  success: { label: "Completed successfully", labelClass: "text-emerald-600", icon: CheckCircle, iconClass: "text-emerald-500" },
  error: { label: "Something went wrong", labelClass: "text-destructive", icon: AlertCircle, iconClass: "text-destructive" },
};

export function PipelineStatus({
  initialStatus,
  lastRunAt,
  organizationsFound,
  emailsFound,
}: PipelineStatusProps) {
  const [status, setStatus] = useState<RunStatus>(initialStatus);
  const ui = STATUS_UI[status];
  const StatusIcon = ui.icon;

  async function handleRun() {
    if (status === "running") return;
    setStatus("running");
    try {
      // TODO: POST /pipeline/run and poll for completion
      await new Promise((r) => setTimeout(r, 3000));
      setStatus("success");
    } catch {
      setStatus("error");
    }
  }

  return (
    <Card className="relative overflow-hidden">
      {status === "running" && (
        <div className="absolute inset-x-0 top-0 h-0.5 bg-blue-500 animate-pulse" />
      )}
      <CardContent className="p-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          {/* Status */}
          <div className="flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
              status === "running" ? "border-blue-300 bg-blue-50" :
              status === "success" ? "border-emerald-200 bg-emerald-50" :
              status === "error" ? "border-red-200 bg-red-50" :
              "border-border bg-muted"
            }`}>
              <StatusIcon className={`h-5 w-5 ${ui.iconClass}`} />
            </div>
            <div>
              <p className={`text-sm font-semibold ${ui.labelClass}`}>{ui.label}</p>
              {formatTime(lastRunAt) ? (
                <p className="text-xs text-muted-foreground">Last run: {formatTime(lastRunAt)}</p>
              ) : (
                <p className="text-xs text-muted-foreground">Never run</p>
              )}
            </div>
          </div>

          {/* Metrics */}
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className="flex items-center gap-1.5 justify-center">
                <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                <p className="text-xl font-semibold tabular-nums">
                  {organizationsFound.toLocaleString()}
                </p>
              </div>
              <p className="text-xs text-muted-foreground">Organizations</p>
            </div>
            <div className="h-8 w-px bg-border" />
            <div className="text-center">
              <div className="flex items-center gap-1.5 justify-center">
                <Mail className="h-3.5 w-3.5 text-primary" />
                <p className="text-xl font-semibold tabular-nums text-primary">
                  {emailsFound.toLocaleString()}
                </p>
              </div>
              <p className="text-xs text-muted-foreground">Emails found</p>
            </div>
          </div>

          {/* Run button */}
          <Button
            size="default"
            onClick={handleRun}
            disabled={status === "running"}
            className="cursor-pointer gap-2 sm:w-auto w-full"
          >
            {status === "running" ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            {status === "running" ? "Running…" : "Run Now"}
          </Button>
        </div>

        {status === "running" && (
          <div className="mt-4 rounded-md bg-blue-50 border border-blue-100 px-4 py-3">
            <p className="text-xs text-blue-700 font-medium">
              Pipeline is running in the background — you can leave this page and come back.
            </p>
          </div>
        )}
        {status === "error" && (
          <div className="mt-4 rounded-md bg-red-50 border border-red-100 px-4 py-3 flex items-start gap-2">
            <AlertCircle className="h-3.5 w-3.5 text-destructive mt-0.5 shrink-0" />
            <p className="text-xs text-destructive">
              The pipeline encountered an error.{" "}
              <button onClick={handleRun} className="underline cursor-pointer font-medium">
                Try again
              </button>{" "}
              or check with your administrator.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
