"use client";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ExternalLink, Mail, Building2, Target } from "lucide-react";
import { CATEGORY_LABELS, CATEGORY_COLORS, type Contact } from "@/lib/types";

interface ContactDetailSheetProps {
  contact: Contact | null;
  onClose: () => void;
}

function InfoRow({ label, value }: { label: string; value: string | null }) {
  if (!value) return null;
  return (
    <div className="space-y-0.5">
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
        {label}
      </p>
      <p className="text-sm">{value}</p>
    </div>
  );
}

function ConfidenceBadge({ score }: { score: number | null }) {
  if (score === null) return null;
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? "text-emerald-700 bg-emerald-50" :
    pct >= 60 ? "text-amber-700 bg-amber-50" :
    "text-red-700 bg-red-50";
  return (
    <Badge variant="secondary" className={`${color} text-xs`}>
      {pct}% confidence
    </Badge>
  );
}

export function ContactDetailSheet({ contact, onClose }: ContactDetailSheetProps) {
  return (
    <Sheet open={!!contact} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-[400px] sm:w-[480px] overflow-y-auto">
        {contact && (
          <>
            <SheetHeader className="space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <SheetTitle className="text-base">
                    {contact.name ?? contact.email}
                  </SheetTitle>
                  {contact.name && (
                    <p className="text-sm text-muted-foreground">{contact.email}</p>
                  )}
                </div>
                {contact.is_targeted && (
                  <Badge className="bg-primary/10 text-primary border-0 gap-1">
                    <Target className="h-3 w-3" />
                    Targeted
                  </Badge>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge
                  variant="secondary"
                  className={`${CATEGORY_COLORS[contact.category]} text-xs`}
                >
                  {CATEGORY_LABELS[contact.category]}
                </Badge>
                {contact.role_type && (
                  <Badge variant="outline" className="text-xs">
                    {contact.role_type.replace("_", " ")}
                  </Badge>
                )}
                <ConfidenceBadge score={contact.confidence} />
              </div>
            </SheetHeader>

            <Separator className="my-4" />

            {/* Contact info */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Mail className="h-3.5 w-3.5 text-muted-foreground" />
                Contact Details
              </div>
              <div className="grid grid-cols-2 gap-3">
                <InfoRow label="Name" value={contact.name} />
                <InfoRow label="Title" value={contact.title} />
                <InfoRow label="Role Type" value={contact.role_type} />
                <InfoRow label="Domain" value={contact.domain} />
              </div>
              {contact.page_url && (
                <a
                  href={contact.page_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline cursor-pointer"
                >
                  <ExternalLink className="h-3 w-3" />
                  View source page
                </a>
              )}
            </div>

            {(contact.org_name || contact.org_description) && (
              <>
                <Separator className="my-4" />
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                    Organization
                  </div>
                  <div className="space-y-3">
                    <InfoRow label="Organization" value={contact.org_name} />
                    {contact.org_description && (
                      <div className="space-y-0.5">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                          Description
                        </p>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                          {contact.org_description}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}

            {contact.sales_notes && (
              <>
                <Separator className="my-4" />
                <div className="space-y-3">
                  <p className="text-sm font-medium">Sales Notes</p>
                  <div className="rounded-md bg-muted/50 p-3 text-sm leading-relaxed text-muted-foreground">
                    {contact.sales_notes}
                  </div>
                </div>
              </>
            )}

            {contact.contact_summary && (
              <>
                <Separator className="my-4" />
                <div className="space-y-3">
                  <p className="text-sm font-medium">Contact Summary</p>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {contact.contact_summary}
                  </p>
                </div>
              </>
            )}

            <Separator className="my-4" />
            <div className="flex gap-2">
              <Button size="sm" className="flex-1 cursor-pointer">
                <Mail className="h-3.5 w-3.5 mr-1.5" />
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
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
