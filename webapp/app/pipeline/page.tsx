import { PipelineStatus } from "@/components/pipeline/pipeline-status";
import { PipelineScheduler } from "@/components/pipeline/pipeline-scheduler";
import { mockPipelineStats } from "@/lib/mock-data";

export default function PipelinePage() {
  // TODO: replace with real status from GET /pipeline/status once backend is ready
  const stats = mockPipelineStats;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Pipeline</h1>
        <p className="text-sm text-muted-foreground">
          Run the pipeline to find organizations and extract their contact emails.
          It runs fully in the background — you don&apos;t need to stay on this page.
        </p>
      </div>

      <PipelineStatus
        initialStatus="success"
        lastRunAt="2026-05-12T14:32:00Z"
        organizationsFound={stats.cleanedDomains}
        emailsFound={stats.extractedContacts}
      />

      <PipelineScheduler />
    </div>
  );
}
