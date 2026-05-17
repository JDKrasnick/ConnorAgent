import { StatsCards } from "@/components/dashboard/stats-cards";
import { PipelineFunnel } from "@/components/dashboard/pipeline-funnel";
import { CategoryBreakdownCard } from "@/components/dashboard/category-breakdown";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import {
  mockPipelineStats,
  mockCategoryBreakdown,
  mockActivityFeed,
} from "@/lib/mock-data";

export default function DashboardPage() {
  // TODO: replace with await fetchPipelineStats() once backend is ready
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Overview</h1>
        <p className="text-sm text-muted-foreground">
          What&apos;s been found and where things stand
        </p>
      </div>

      <StatsCards stats={mockPipelineStats} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <PipelineFunnel stats={mockPipelineStats} />
        <CategoryBreakdownCard data={mockCategoryBreakdown} />
      </div>

      <ActivityFeed events={mockActivityFeed} />
    </div>
  );
}
