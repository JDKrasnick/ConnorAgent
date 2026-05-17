import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Building2, ExternalLink, Mail, MessageCircle, Send, Target } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { buttonVariants } from "@/components/ui/button";
import { mockContacts, mockOutreachRecords } from "@/lib/mock-data";
import {
  CATEGORY_COLORS,
  CATEGORY_LABELS,
  type Contact,
  type OutreachRecord,
} from "@/lib/types";
import { cn } from "@/lib/utils";

interface ContactProfilePageProps {
  params: Promise<{ id: string }>;
}

const OUTREACH_STATUS: Record<
  OutreachRecord["status"] | "not_sent",
  { label: string; className: string }
> = {
  not_sent: { label: "Not sent email", className: "bg-zinc-100 text-zinc-700" },
  pending: { label: "Not sent email", className: "bg-zinc-100 text-zinc-700" },
  sent: { label: "Email sent", className: "bg-blue-100 text-blue-700" },
  replied: { label: "In talks", className: "bg-emerald-100 text-emerald-700" },
  bounced: { label: "Email sent", className: "bg-red-100 text-red-700" },
};

function InfoRow({ label, value }: { label: string; value: string | null }) {
  if (!value) return null;
  return (
    <div className="space-y-1">
      <p className="text-xs font-medium uppercase text-muted-foreground">{label}</p>
      <p className="text-sm">{value}</p>
    </div>
  );
}

function formatDate(iso: string | null) {
  if (!iso) return "Not recorded";
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function confidenceLabel(contact: Contact) {
  if (contact.confidence === null) return null;
  return `${Math.round(contact.confidence * 100)}% confidence`;
}

export default async function ContactProfilePage({ params }: ContactProfilePageProps) {
  const { id } = await params;
  const contact = mockContacts.find((item) => item.id === id);
  if (!contact) notFound();

  const record = mockOutreachRecords.find((item) => item.contact.id === contact.id) ?? null;
  const outreachStatus = OUTREACH_STATUS[record?.status ?? "not_sent"];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-3">
          <Link
            href="/contacts"
            className={cn(buttonVariants({ variant: "ghost", size: "sm" }), "w-fit")}
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Contacts
          </Link>
          <div>
            <h1 className="text-xl font-semibold">{contact.name ?? contact.email}</h1>
            {contact.name && (
              <p className="text-sm text-muted-foreground">{contact.email}</p>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge
              variant="secondary"
              className={`text-xs ${CATEGORY_COLORS[contact.category]}`}
            >
              {CATEGORY_LABELS[contact.category]}
            </Badge>
            <Badge variant="secondary" className={`text-xs ${outreachStatus.className}`}>
              {outreachStatus.label}
            </Badge>
            {contact.is_targeted && (
              <Badge className="gap-1 border-0 bg-primary/10 text-primary">
                <Target className="h-3 w-3" />
                Targeted
              </Badge>
            )}
            {confidenceLabel(contact) && (
              <Badge variant="outline" className="text-xs">
                {confidenceLabel(contact)}
              </Badge>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <Button size="sm" className="cursor-pointer">
            <Mail className="h-3.5 w-3.5" />
            Send Outreach
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="cursor-pointer"
            render={
              <a
                href={`mailto:${contact.email}`}
                target="_blank"
                rel="noopener noreferrer"
              />
            }
          >
            Open in Mail
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-semibold">
                <Mail className="h-4 w-4 text-muted-foreground" />
                Contact
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <InfoRow label="Name" value={contact.name} />
                <InfoRow label="Title" value={contact.title} />
                <InfoRow label="Email" value={contact.email} />
                <InfoRow label="Role type" value={contact.role_type?.replace("_", " ") ?? null} />
                <InfoRow label="Domain" value={contact.domain} />
                <InfoRow label="Extracted" value={formatDate(contact.extracted_at)} />
              </div>
              {contact.page_url && (
                <>
                  <Separator />
                  <a
                    href={contact.page_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline"
                  >
                    <ExternalLink className="h-3 w-3" />
                    View source page
                  </a>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-semibold">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                Organization
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <InfoRow label="Organization" value={contact.org_name ?? contact.domain} />
              {contact.org_description && (
                <div className="space-y-1">
                  <p className="text-xs font-medium uppercase text-muted-foreground">
                    Description
                  </p>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {contact.org_description}
                  </p>
                </div>
              )}
              {contact.sales_notes && (
                <>
                  <Separator />
                  <div className="space-y-1">
                    <p className="text-xs font-medium uppercase text-muted-foreground">
                      Sales notes
                    </p>
                    <p className="text-sm leading-relaxed text-muted-foreground">
                      {contact.sales_notes}
                    </p>
                  </div>
                </>
              )}
              {contact.contact_summary && (
                <>
                  <Separator />
                  <div className="space-y-1">
                    <p className="text-xs font-medium uppercase text-muted-foreground">
                      Contact summary
                    </p>
                    <p className="text-sm leading-relaxed text-muted-foreground">
                      {contact.contact_summary}
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="h-fit">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-semibold">
              <MessageCircle className="h-4 w-4 text-muted-foreground" />
              Outreach
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <InfoRow label="Status" value={outreachStatus.label} />
            <InfoRow label="Subject" value={record?.subject ?? "No email generated yet"} />
            <InfoRow label="Sent" value={formatDate(record?.sent_at ?? null)} />
            <InfoRow label="Replied" value={formatDate(record?.replied_at ?? null)} />
            <Separator />
            <div className="rounded-md bg-muted/50 p-3">
              <div className="flex items-start gap-2">
                <Send className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                <p className="text-xs leading-relaxed text-muted-foreground">
                  Email generation, Gmail sending, and reply sync are planned backend integrations.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
