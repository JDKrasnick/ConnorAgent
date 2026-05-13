"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { CalendarClock, Check } from "lucide-react";

const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] as const;
type Day = (typeof DAYS)[number];

function nextOccurrence(days: Day[], time: string): string | null {
  if (days.length === 0 || !time) return null;
  const [h, m] = time.split(":").map(Number);
  const dayIndices = days.map((d) => DAYS.indexOf(d));
  const now = new Date();
  for (let offset = 0; offset < 8; offset++) {
    const candidate = new Date(now);
    candidate.setDate(now.getDate() + offset);
    candidate.setHours(h, m, 0, 0);
    if (
      candidate > now &&
      dayIndices.includes(candidate.getDay())
    ) {
      return candidate.toLocaleString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
    }
  }
  return null;
}

export function PipelineScheduler() {
  const [enabled, setEnabled] = useState(false);
  const [time, setTime] = useState("06:00");
  const [selectedDays, setSelectedDays] = useState<Day[]>(["Mon", "Wed", "Fri"]);
  const [saved, setSaved] = useState(false);

  function toggleDay(day: Day) {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
    setSaved(false);
  }

  async function handleSave() {
    // TODO: POST /pipeline/schedule { days: selectedDays, time, enabled }
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  const next = enabled ? nextOccurrence(selectedDays, time) : null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CalendarClock className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold">Scheduled Runs</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">
              {enabled ? "On" : "Off"}
            </span>
            <Switch
              checked={enabled}
              onCheckedChange={(v) => { setEnabled(v); setSaved(false); }}
            />
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        <div
          className={`space-y-5 transition-opacity ${
            enabled ? "opacity-100" : "opacity-40 pointer-events-none select-none"
          }`}
        >
          {/* Time picker */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Run at
            </label>
            <input
              type="time"
              value={time}
              onChange={(e) => { setTime(e.target.value); setSaved(false); }}
              className="flex h-8 w-36 rounded-md border bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>

          {/* Day selector */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Repeat on
            </label>
            <div className="flex flex-wrap gap-1.5">
              {DAYS.map((day) => {
                const active = selectedDays.includes(day);
                return (
                  <button
                    key={day}
                    onClick={() => toggleDay(day)}
                    className={`h-8 w-10 rounded-md text-xs font-medium transition-colors cursor-pointer border ${
                      active
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background text-muted-foreground border-border hover:bg-muted"
                    }`}
                  >
                    {day}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Next run preview */}
          {next && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <CalendarClock className="h-3.5 w-3.5" />
              Next run: <span className="text-foreground font-medium">{next}</span>
            </div>
          )}
          {enabled && selectedDays.length === 0 && (
            <p className="text-xs text-muted-foreground">Select at least one day.</p>
          )}
        </div>

        <Button
          size="sm"
          variant={saved ? "outline" : "default"}
          onClick={handleSave}
          disabled={enabled && selectedDays.length === 0}
          className="cursor-pointer gap-1.5 w-full sm:w-auto"
        >
          {saved ? (
            <>
              <Check className="h-3.5 w-3.5 text-emerald-500" />
              Saved
            </>
          ) : (
            "Save Schedule"
          )}
        </Button>

        {!enabled && (
          <p className="text-xs text-muted-foreground">
            Enable scheduling to run the pipeline automatically at a set time.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
