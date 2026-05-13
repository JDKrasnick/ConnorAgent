"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Loader2, Send } from "lucide-react";
import type { Contact } from "@/lib/types";

interface ComposeModalProps {
  contact: Contact | null;
  onClose: () => void;
  onSent?: (contactId: string) => void;
}

export function ComposeModal({ contact, onClose, onSent }: ComposeModalProps) {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [sending, setSending] = useState(false);

  async function handleSend() {
    if (!contact || !subject || !body) return;
    setSending(true);
    try {
      // TODO: call sendOutreachEmail({ contact_id: contact.id, subject, body })
      await new Promise((r) => setTimeout(r, 1200)); // placeholder
      onSent?.(contact.id);
      onClose();
    } finally {
      setSending(false);
    }
  }

  return (
    <Dialog open={!!contact} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[540px]">
        <DialogHeader>
          <DialogTitle className="text-base">Compose Outreach</DialogTitle>
        </DialogHeader>

        {contact && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 rounded-md bg-muted/50 p-3">
              <span className="text-xs text-muted-foreground">To:</span>
              <span className="text-sm font-medium">{contact.name ?? contact.email}</span>
              <span className="text-xs text-muted-foreground">&lt;{contact.email}&gt;</span>
              {contact.org_name && (
                <Badge variant="secondary" className="ml-auto text-xs">
                  {contact.org_name}
                </Badge>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Subject
              </label>
              <Input
                placeholder="e.g. Quick question about your program"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="text-sm"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Message
              </label>
              <textarea
                placeholder="Write your message..."
                value={body}
                onChange={(e) => setBody(e.target.value)}
                rows={8}
                className="w-full rounded-md border bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-none"
              />
            </div>

            {contact.sales_notes && (
              <div className="rounded-md bg-primary/5 border border-primary/20 p-3">
                <p className="text-xs font-medium text-primary mb-1">Sales context</p>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {contact.sales_notes}
                </p>
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="ghost" onClick={onClose} className="cursor-pointer">
            Cancel
          </Button>
          <Button
            onClick={handleSend}
            disabled={sending || !subject || !body}
            className="cursor-pointer gap-1.5"
          >
            {sending ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Send className="h-3.5 w-3.5" />
            )}
            Send Email
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
