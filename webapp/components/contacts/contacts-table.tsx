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
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Target, ChevronUp, ChevronDown, Search, X } from "lucide-react";
import { CATEGORY_LABELS, CATEGORY_COLORS, type Contact, type Category } from "@/lib/types";
import { ContactDetailSheet } from "./contact-detail-sheet";

const ROLE_TYPES = ["decision_maker", "faculty", "coordinator", "generic"] as const;

function ConfidenceDot({ score }: { score: number | null }) {
  if (score === null) return <span className="text-muted-foreground">—</span>;
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? "bg-emerald-500" :
    pct >= 60 ? "bg-amber-500" :
    "bg-red-500";
  return (
    <div className="flex items-center gap-1.5">
      <div className={`h-2 w-2 rounded-full ${color}`} />
      <span className="text-xs tabular-nums">{pct}%</span>
    </div>
  );
}

type SortKey = "name" | "domain" | "category" | "confidence" | "extracted_at";
type SortDir = "asc" | "desc";

interface ContactsTableProps {
  contacts: Contact[];
}

export function ContactsTable({ contacts }: ContactsTableProps) {
  const [selected, setSelected] = useState<Contact | null>(null);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [targetedOnly, setTargetedOnly] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("extracted_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  const filtered = contacts
    .filter((c) => {
      if (search) {
        const q = search.toLowerCase();
        if (
          !c.email.toLowerCase().includes(q) &&
          !(c.name ?? "").toLowerCase().includes(q) &&
          !c.domain.toLowerCase().includes(q)
        )
          return false;
      }
      if (categoryFilter !== "all" && c.category !== categoryFilter) return false;
      if (roleFilter !== "all" && c.role_type !== roleFilter) return false;
      if (targetedOnly && !c.is_targeted) return false;
      return true;
    })
    .sort((a, b) => {
      let av: string | number = a[sortKey] ?? "";
      let bv: string | number = b[sortKey] ?? "";
      if (sortKey === "confidence") {
        av = a.confidence ?? -1;
        bv = b.confidence ?? -1;
      }
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });

  function SortIcon({ col }: { col: SortKey }) {
    if (sortKey !== col) return <ChevronUp className="h-3 w-3 opacity-20" />;
    return sortDir === "asc" ? (
      <ChevronUp className="h-3 w-3" />
    ) : (
      <ChevronDown className="h-3 w-3" />
    );
  }

  function SortableHead({
    col,
    children,
  }: {
    col: SortKey;
    children: React.ReactNode;
  }) {
    return (
      <TableHead>
        <button
          onClick={() => handleSort(col)}
          className="flex items-center gap-1 cursor-pointer hover:text-foreground transition-colors"
        >
          {children}
          <SortIcon col={col} />
        </button>
      </TableHead>
    );
  }

  const hasFilters = search || categoryFilter !== "all" || roleFilter !== "all" || targetedOnly;

  return (
    <>
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            placeholder="Search name, email, domain..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8 h-8 text-sm"
          />
        </div>

        <Select value={categoryFilter} onValueChange={(v) => setCategoryFilter(v ?? "all")}>
          <SelectTrigger className="h-8 w-[160px] text-sm cursor-pointer">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {(Object.keys(CATEGORY_LABELS) as Category[]).map((cat) => (
              <SelectItem key={cat} value={cat}>
                {CATEGORY_LABELS[cat]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={roleFilter} onValueChange={(v) => setRoleFilter(v ?? "all")}>
          <SelectTrigger className="h-8 w-[160px] text-sm cursor-pointer">
            <SelectValue placeholder="Role type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All roles</SelectItem>
            {ROLE_TYPES.map((r) => (
              <SelectItem key={r} value={r}>
                {r.replace("_", " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button
          variant={targetedOnly ? "default" : "outline"}
          size="sm"
          onClick={() => setTargetedOnly((v) => !v)}
          className="h-8 gap-1.5 cursor-pointer"
        >
          <Target className="h-3.5 w-3.5" />
          Targeted only
        </Button>

        {hasFilters && (
          <Button
            variant="ghost"
            size="sm"
            className="h-8 text-muted-foreground cursor-pointer"
            onClick={() => {
              setSearch("");
              setCategoryFilter("all");
              setRoleFilter("all");
              setTargetedOnly(false);
            }}
          >
            <X className="h-3.5 w-3.5 mr-1" />
            Clear
          </Button>
        )}

        <span className="ml-auto text-xs text-muted-foreground tabular-nums">
          {filtered.length.toLocaleString()} contacts
        </span>
      </div>

      {/* Table */}
      <div className="rounded-md border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/30 hover:bg-muted/30">
              <SortableHead col="name">Name / Email</SortableHead>
              <SortableHead col="domain">Domain</SortableHead>
              <SortableHead col="category">Category</SortableHead>
              <TableHead>Role</TableHead>
              <TableHead>Targeted</TableHead>
              <SortableHead col="confidence">Confidence</SortableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-10">
                  No contacts match your filters.
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((contact) => (
                <TableRow
                  key={contact.id}
                  onClick={() => setSelected(contact)}
                  className="cursor-pointer hover:bg-muted/40 transition-colors"
                >
                  <TableCell>
                    <div>
                      <p className="text-sm font-medium">
                        {contact.name ?? (
                          <span className="text-muted-foreground italic">Unnamed</span>
                        )}
                      </p>
                      <p className="text-xs text-muted-foreground">{contact.email}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground font-mono">
                    {contact.domain}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="secondary"
                      className={`text-xs ${CATEGORY_COLORS[contact.category]}`}
                    >
                      {CATEGORY_LABELS[contact.category]}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {contact.role_type ? (
                      <Badge variant="outline" className="text-xs">
                        {contact.role_type.replace("_", " ")}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {contact.is_targeted ? (
                      <Badge className="bg-primary/10 text-primary border-0 text-xs gap-1">
                        <Target className="h-2.5 w-2.5" />
                        Yes
                      </Badge>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <ConfidenceDot score={contact.confidence} />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <ContactDetailSheet contact={selected} onClose={() => setSelected(null)} />
    </>
  );
}
