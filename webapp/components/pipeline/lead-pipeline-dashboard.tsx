import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  CATEGORY_COLORS,
  CATEGORY_LABELS,
  type Contact,
  type OutreachRecord,
} from "@/lib/types";
import { Mail, MailCheck, MessageCircle, Send, UserRound } from "lucide-react";
import Link from "next/link";

type LeadStatus = "not_sent" | "email_sent" | "in_talks";

interface LeadPipelineDashboardProps {
  contacts: Contact[];
  records: OutreachRecord[];
}

interface LeadRow {
  contact: Contact;
  record: OutreachRecord | null;
  status: LeadStatus;
}

const STATUS_COLUMNS: Array<{
  id: LeadStatus;
  label: string;
  description: string;
  icon: typeof Mail;
  badgeClassName: string;
}> = [
  {
    id: "not_sent",
    label: "Not Sent Email",
    description: "Ready for generated outreach",
    icon: Mail,
    badgeClassName: "bg-zinc-100 text-zinc-700",
  },
  {
    id: "email_sent",
    label: "Email Sent",
    description: "Waiting for a reply",
    icon: MailCheck,
    badgeClassName: "bg-blue-100 text-blue-700",
  },
  {
    id: "in_talks",
    label: "In Talks",
    description: "Lead replied",
    icon: MessageCircle,
    badgeClassName: "bg-emerald-100 text-emerald-700",
  },
];

function formatDate(iso: string | null) {
  if (!iso) return "No activity yet";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function getLeadStatus(record: OutreachRecord | null): LeadStatus {
  if (!record) return "not_sent";
  if (record.status === "replied") return "in_talks";
  if (record.sent_at) return "email_sent";
  return "not_sent";
}

function LeadCard({ lead }: { lead: LeadRow }) {
  const { contact, record, status } = lead;
  const activityDate =
    status === "in_talks" ? record?.replied_at ?? record?.sent_at ?? null : record?.sent_at ?? null;

  return (
    <Link
      href={`/contacts/${contact.id}`}
      className="block rounded-md border bg-background p-3 shadow-sm transition-colors hover:bg-muted/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium">
            {contact.name ?? "Unnamed lead"}
          </p>
          <p className="truncate text-xs text-muted-foreground">{contact.email}</p>
        </div>
        <Badge
          variant="secondary"
          className={`shrink-0 text-xs ${CATEGORY_COLORS[contact.category]}`}
        >
          {CATEGORY_LABELS[contact.category]}
        </Badge>
      </div>

      <div className="mt-3 space-y-2 text-xs text-muted-foreground">
        <div className="flex items-start gap-2">
          <UserRound className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span className="min-w-0 truncate">
            {contact.title ?? contact.role_type?.replace("_", " ") ?? "Lead"}
          </span>
        </div>
        <div className="flex items-start gap-2">
          <Send className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span className="min-w-0 truncate">
            {record?.subject ?? "No email generated yet"}
          </span>
        </div>
      </div>

      <div className="mt-3 border-t pt-2">
        <p className="truncate text-xs text-muted-foreground">
          {contact.org_name ?? contact.domain}
        </p>
        <p className="mt-1 text-xs font-medium tabular-nums">
          {formatDate(activityDate)}
        </p>
      </div>
    </Link>
  );
}

export function LeadPipelineDashboard({
  contacts,
  records,
}: LeadPipelineDashboardProps) {
  const recordByContactId = new Map(records.map((record) => [record.contact.id, record]));
  const leads = contacts
    .filter((contact) => contact.is_targeted)
    .map((contact) => {
      const record = recordByContactId.get(contact.id) ?? null;
      return {
        contact,
        record,
        status: getLeadStatus(record),
      };
    });

  const groupedLeads = STATUS_COLUMNS.map((column) => ({
    ...column,
    leads: leads.filter((lead) => lead.status === column.id),
  }));

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">Lead Dashboard</CardTitle>
        <p className="text-xs text-muted-foreground">
          Track each targeted lead from pending outreach to active conversations.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-3">
          {groupedLeads.map(({ id, label, icon: Icon, badgeClassName, leads }) => (
            <div key={id} className="rounded-md border bg-muted/30 p-3">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <p className="text-xs font-medium">{label}</p>
                </div>
                <Badge variant="secondary" className={`text-xs ${badgeClassName}`}>
                  {leads.length}
                </Badge>
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          {groupedLeads.map(
            ({ id, label, description, icon: Icon, badgeClassName, leads }) => (
              <section key={id} className="min-w-0 rounded-md border bg-muted/20">
                <div className="flex items-start justify-between gap-3 border-b p-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                      <h2 className="text-sm font-semibold">{label}</h2>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">{description}</p>
                  </div>
                  <Badge variant="secondary" className={`text-xs ${badgeClassName}`}>
                    {leads.length}
                  </Badge>
                </div>

                <div className="space-y-3 p-3">
                  {leads.length > 0 ? (
                    leads.map((lead) => (
                      <LeadCard key={lead.contact.id} lead={lead} />
                    ))
                  ) : (
                    <div className="rounded-md border border-dashed bg-background/70 px-3 py-8 text-center">
                      <p className="text-xs text-muted-foreground">No leads in this stage.</p>
                    </div>
                  )}
                </div>
              </section>
            )
          )}
        </div>
      </CardContent>
    </Card>
  );
}
