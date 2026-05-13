"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Loader2 } from "lucide-react";

// Gmail SVG logo
function GmailIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden="true">
      <path
        d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z"
        fill="#EA4335"
      />
    </svg>
  );
}

interface GmailConnectBannerProps {
  isConnected: boolean;
  connectedEmail?: string;
}

export function GmailConnectBanner({ isConnected, connectedEmail }: GmailConnectBannerProps) {
  const [loading, setLoading] = useState(false);

  async function handleConnect() {
    setLoading(true);
    try {
      // TODO: call getGmailAuthUrl() and redirect to OAuth URL
      // const { url } = await getGmailAuthUrl();
      // window.location.href = url;
      await new Promise((r) => setTimeout(r, 1000)); // placeholder
    } finally {
      setLoading(false);
    }
  }

  if (isConnected) {
    return (
      <Card className="border-emerald-200 bg-emerald-50">
        <CardContent className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="h-4 w-4 text-emerald-600" />
            <div>
              <p className="text-sm font-medium text-emerald-900">Gmail connected</p>
              {connectedEmail && (
                <p className="text-xs text-emerald-700">{connectedEmail}</p>
              )}
            </div>
          </div>
          <Button variant="outline" size="sm" className="text-xs cursor-pointer border-emerald-300 hover:bg-emerald-100">
            Disconnect
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-dashed">
      <CardContent className="flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          <GmailIcon />
          <div>
            <p className="text-sm font-medium">Connect Gmail</p>
            <p className="text-xs text-muted-foreground">
              Required to send outreach emails from this app
            </p>
          </div>
          <Badge variant="secondary" className="text-xs ml-1">OAuth</Badge>
        </div>
        <Button
          size="sm"
          onClick={handleConnect}
          disabled={loading}
          className="cursor-pointer"
        >
          {loading ? (
            <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
          ) : (
            <GmailIcon />
          )}
          <span className="ml-1.5">Connect Gmail</span>
        </Button>
      </CardContent>
    </Card>
  );
}
