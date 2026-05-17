import { ContactsTable } from "@/components/contacts/contacts-table";
import { mockContacts } from "@/lib/mock-data";

export default function ContactsPage() {
  // TODO: replace with await fetchContacts() once backend is ready
  const contacts = mockContacts;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold">Contacts</h1>
        <p className="text-sm text-muted-foreground">
          Extracted contacts from crawled domains. Click a row for details.
        </p>
      </div>
      <ContactsTable contacts={contacts} />
    </div>
  );
}
