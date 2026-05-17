import { PipelineStatus } from "@/components/pipeline/pipeline-status";
import { LeadPipelineDashboard } from "@/components/pipeline/lead-pipeline-dashboard";
import {
  mockContacts,
  mockOutreachRecords,
  mockPipelineStats,
} from "@/lib/mock-data";

export default function PipelinePage() {
  // TODO: replace with real status from GET /pipeline/status once backend is ready
  const stats = mockPipelineStats;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Pipeline</h1>
        <p className="text-sm text-muted-foreground">
          Run the pipeline, then track where each lead stands in outreach.
        </p>
      </div>

      <PipelineStatus
        initialStatus="success"
        lastRunAt="2026-05-12T14:32:00Z"
        organizationsFound={stats.cleanedDomains}
        emailsFound={stats.extractedContacts}
      />

      <LeadPipelineDashboard
        contacts={mockContacts}
        records={mockOutreachRecords}
      />
    </div>
  );
}
