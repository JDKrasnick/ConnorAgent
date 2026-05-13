"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import {
  Send,
  MessageCircle,
  Clock,
  MailCheck,
  TrendingUp,
  AlertCircle,
} from "lucide-react";
import { CATEGORY_LABELS, CATEGORY_COLORS, type OutreachRecord } from "@/lib/types";
import { ComposeModal } from "./compose-modal";
import type { Contact } from "@/lib/types";

const STATUS_CONFIG = {
  pending: {
    label: "Not sent",
    className: "bg-zinc-100 text-zinc-700",
    icon: Clock,
  },
  sent: {
    label: "Sent",
    className: "bg-blue-100 text-blue-700",
    icon: MailCheck,
  },
  replied: {
    label: "Replied",
    className: "bg-emerald-100 text-emerald-700",
    icon: MessageCircle,
  },
  bounced: {
    label: "Bounced",
    className: "bg-red-100 text-red-700",
    icon: AlertCircle,
  },
};

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

interface OutreachStats {
  ready: number;
  sent: number;
  replied: number;
  bounced: number;
  replyRate: string;
}

function OutreachStatCards({ stats }: { stats: OutreachStats }) {
  const items = [
    { label: "Ready to Send", value: stats.ready, icon: Clock, color: "text-muted-foreground" },
    { label: "Emails Sent", value: stats.sent, icon: Send, color: "text-blue-600" },
    { label: "Replies", value: stats.replied, icon: MessageCircle, color: "text-emerald-600" },
    { label: "Reply Rate", value: stats.replyRate, icon: TrendingUp, color: "text-primary" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {items.map(({ label, value, icon: Icon, color }) => (
        <Card key={label}>
          <CardContent className="p-4 flex items-center gap-3">
            <Icon className={`h-5 w-5 ${color} shrink-0`} />
            <div>
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-lg font-semibold tabular-nums">
                {typeof value === "number" ? value.toLocaleString() : value}
              </p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function ContactRow({
  contact,
  selected,
  onToggle,
  onCompose,
}: {
  contact: Contact;
  selected: boolean;
  onToggle: () => void;
  onCompose: () => void;
}) {
  return (
    <TableRow>
      <TableCell className="w-10">
        <Checkbox checked={selected} onCheckedChange={onToggle} />
      </TableCell>
      <TableCell>
        <div>
          <p className="text-sm font-medium">{contact.name ?? "Unnamed contact"}</p>
          <p className="text-xs text-muted-foreground">{contact.email}</p>
        </div>
      </TableCell>
      <TableCell className="text-xs text-muted-foreground">
        {contact.org_name ?? contact.domain}
      </TableCell>
      <TableCell>
        <Badge
          variant="secondary"
          className={`text-xs ${CATEGORY_COLORS[contact.category]}`}
        >
          {CATEGORY_LABELS[contact.category]}
        </Badge>
      </TableCell>
      <TableCell className="text-xs text-muted-foreground capitalize">
        {contact.role_type?.replace("_", " ") ?? "—"}
      </TableCell>
      <TableCell className="text-right">
        <Button
          size="sm"
          variant="default"
          onClick={onCompose}
          className="h-7 cursor-pointer gap-1"
        >
          <Send className="h-3 w-3" />
          Compose
        </Button>
      </TableCell>
    </TableRow>
  );
}

function HistoryRow({ record }: { record: OutreachRecord }) {
  const cfg = STATUS_CONFIG[record.status];
  const StatusIcon = cfg.icon;
  return (
    <TableRow>
      <TableCell>
        <div>
          <p className="text-sm font-medium">
            {record.contact.name ?? "Unnamed contact"}
          </p>
          <p className="text-xs text-muted-foreground">{record.contact.email}</p>
        </div>
      </TableCell>
      <TableCell className="text-xs text-muted-foreground">
        {record.contact.org_name ?? record.contact.domain}
      </TableCell>
      <TableCell className="text-sm text-muted-foreground max-w-[200px] truncate">
        {record.subject ?? "—"}
      </TableCell>
      <TableCell>
        <Badge variant="secondary" className={`text-xs gap-1 ${cfg.className}`}>
          <StatusIcon className="h-2.5 w-2.5" />
          {cfg.label}
        </Badge>
      </TableCell>
      <TableCell className="text-xs text-muted-foreground tabular-nums">
        {formatDate(record.sent_at)}
      </TableCell>
      <TableCell className="text-xs text-muted-foreground tabular-nums">
        {formatDate(record.replied_at)}
      </TableCell>
    </TableRow>
  );
}

interface OutreachTableProps {
  records: OutreachRecord[];
  pendingContacts: Contact[];
}

export function OutreachTable({ records, pendingContacts }: OutreachTableProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [composeTarget, setComposeTarget] = useState<Contact | null>(null);

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  const sent = records.filter((r) => r.status !== "pending");
  const replied = records.filter((r) => r.status === "replied");
  const bounced = records.filter((r) => r.status === "bounced");
  const sentCount = records.filter((r) => r.status === "sent" || r.status === "replied" || r.status === "bounced").length;
  const replyRate = sentCount > 0 ? `${Math.round((replied.length / sentCount) * 100)}%` : "—";

  const stats: OutreachStats = {
    ready: pendingContacts.length,
    sent: sentCount,
    replied: replied.length,
    bounced: bounced.length,
    replyRate,
  };

  const allForTab = [...pendingContacts.map((c) => ({ type: "pending" as const, contact: c }))];

  return (
    <>
      <OutreachStatCards stats={stats} />

      <Tabs defaultValue="ready">
        <TabsList className="mb-4">
          <TabsTrigger value="ready" className="cursor-pointer gap-1.5">
            <Clock className="h-3.5 w-3.5" />
            Ready to Send
            {pendingContacts.length > 0 && (
              <Badge variant="secondary" className="ml-1 text-xs h-4 px-1">
                {pendingContacts.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="sent" className="cursor-pointer gap-1.5">
            <Send className="h-3.5 w-3.5" />
            Sent
            {sent.length > 0 && (
              <Badge variant="secondary" className="ml-1 text-xs h-4 px-1">
                {sent.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="replied" className="cursor-pointer gap-1.5">
            <MessageCircle className="h-3.5 w-3.5" />
            Replied
            {replied.length > 0 && (
              <Badge variant="secondary" className="ml-1 text-xs h-4 px-1 bg-emerald-100 text-emerald-700">
                {replied.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Ready to send */}
        <TabsContent value="ready">
          {allForTab.length === 0 ? (
            <div className="rounded-lg border border-dashed py-12 text-center">
              <p className="text-sm text-muted-foreground">No contacts ready to send yet.</p>
              <p className="text-xs text-muted-foreground mt-1">Run the pipeline to find more contacts.</p>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-muted-foreground">
                  {selectedIds.size > 0
                    ? `${selectedIds.size} selected`
                    : `${pendingContacts.length} contacts ready`}
                </p>
                {selectedIds.size > 0 && (
                  <Button size="sm" className="cursor-pointer gap-1.5">
                    <Send className="h-3.5 w-3.5" />
                    Send to {selectedIds.size} contacts
                  </Button>
                )}
              </div>
              <div className="rounded-md border overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted/30 hover:bg-muted/30">
                      <TableHead className="w-10">
                        <Checkbox
                          checked={
                            selectedIds.size === pendingContacts.length &&
                            pendingContacts.length > 0
                          }
                          onCheckedChange={(checked) => {
                            if (checked)
                              setSelectedIds(new Set(pendingContacts.map((c) => c.id)));
                            else setSelectedIds(new Set());
                          }}
                        />
                      </TableHead>
                      <TableHead>Contact</TableHead>
                      <TableHead>Organization</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingContacts.map((contact) => (
                      <ContactRow
                        key={contact.id}
                        contact={contact}
                        selected={selectedIds.has(contact.id)}
                        onToggle={() => toggleSelect(contact.id)}
                        onCompose={() => setComposeTarget(contact)}
                      />
                    ))}
                  </TableBody>
                </Table>
              </div>
            </>
          )}
        </TabsContent>

        {/* Sent */}
        <TabsContent value="sent">
          <div className="rounded-md border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/30 hover:bg-muted/30">
                  <TableHead>Contact</TableHead>
                  <TableHead>Organization</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Sent</TableHead>
                  <TableHead>Replied</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sent.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-10">
                      No emails sent yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  sent.map((record) => <HistoryRow key={record.id} record={record} />)
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        {/* Replied */}
        <TabsContent value="replied">
          <div className="rounded-md border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/30 hover:bg-muted/30">
                  <TableHead>Contact</TableHead>
                  <TableHead>Organization</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Sent</TableHead>
                  <TableHead>Replied</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {replied.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-10">
                      No replies yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  replied.map((record) => <HistoryRow key={record.id} record={record} />)
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>

      <ComposeModal
        contact={composeTarget}
        onClose={() => setComposeTarget(null)}
      />
    </>
  );
}
