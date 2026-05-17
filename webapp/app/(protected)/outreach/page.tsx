import { GmailConnectBanner } from "@/components/outreach/gmail-connect";
import { OutreachTable } from "@/components/outreach/outreach-table";
import { mockOutreachRecords, mockContacts } from "@/lib/mock-data";

// TODO: replace with real data from fetchContacts({ is_targeted: true }) + outreach records
const targetedContacts = mockContacts.filter(
  (c) => c.is_targeted && !mockOutreachRecords.some((r) => r.contact.id === c.id)
);

export default function OutreachPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Outreach</h1>
        <p className="text-sm text-muted-foreground">
          Manage and send outreach emails to extracted contacts.
        </p>
      </div>

      {/* TODO: pass isConnected=true and connectedEmail once OAuth is implemented */}
      <GmailConnectBanner isConnected={false} />

      <OutreachTable
        records={mockOutreachRecords}
        pendingContacts={targetedContacts}
      />
    </div>
  );
}
