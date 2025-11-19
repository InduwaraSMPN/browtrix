"use client";

import { useEffect, useState } from "react";
import { useBrowtrix } from "@/lib/browtrix-context";
import { captureSnapshot } from "@/lib/snapshot";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

interface RequestState {
  id: string;
  type: "SHOW_CONFIRM" | "SHOW_INPUT";
  msg: string;
  validation?: string;
}

export function BrowtrixOverlay() {
  const { lastMessage, sendMessage, isConnected } = useBrowtrix();
  const [activeRequest, setActiveRequest] = useState<RequestState | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!lastMessage) return;
    const { type, id, msg, validation } = lastMessage;

    if (type === "GET_SNAPSHOT") {
      // Handle snapshot immediately without UI
      try {
        const content = captureSnapshot();
        sendMessage({ type: "SNAPSHOT_RESULT", id, content });
      } catch (e) {
        sendMessage({ type: "ERROR", id, msg: "Failed to capture snapshot" });
      }
    } else if (type === "SHOW_CONFIRM") {
      setActiveRequest({ id, type, msg });
    } else if (type === "SHOW_INPUT") {
      setActiveRequest({ id, type, msg, validation });
      setInputValue("");
      setError("");
    } else if (type === "ABORT_UI") {
        if (activeRequest && activeRequest.id === id) {
            setActiveRequest(null);
        }
    }
  }, [lastMessage]);

  const handleConfirm = (approved: boolean) => {
    if (!activeRequest) return;
    sendMessage({
      type: "CONFIRM_RESULT",
      id: activeRequest.id,
      approved,
    });
    setActiveRequest(null);
  };

  const handleInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeRequest) return;

    // Simple validation
    if (activeRequest.validation === "email") {
       const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
       if (!emailRegex.test(inputValue)) {
           setError("Invalid email address");
           return;
       }
    }

    sendMessage({
      type: "INPUT_RESULT",
      id: activeRequest.id,
      value: inputValue,
    });
    setActiveRequest(null);
  };

  if (!activeRequest) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle>
            {activeRequest.type === "SHOW_CONFIRM" ? "Confirmation Request" : "Input Request"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">{activeRequest.msg}</p>
          
          {activeRequest.type === "SHOW_INPUT" && (
            <form id="browtrix-form" onSubmit={handleInputSubmit}>
              <Input
                value={inputValue}
                onChange={(e) => {
                    setInputValue(e.target.value);
                    setError("");
                }}
                placeholder="Enter your answer..."
                autoFocus
              />
              {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
            </form>
          )}
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          {activeRequest.type === "SHOW_CONFIRM" ? (
            <>
              <Button variant="outline" onClick={() => handleConfirm(false)}>
                No / Deny
              </Button>
              <Button onClick={() => handleConfirm(true)}>Yes / Approve</Button>
            </>
          ) : (
            <>
              <Button variant="outline" onClick={() => setActiveRequest(null)}>
                Cancel
              </Button>
              <Button type="submit" form="browtrix-form">
                Submit
              </Button>
            </>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
