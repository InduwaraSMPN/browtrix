"use client";

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from "react";

interface BrowtrixContextType {
  isConnected: boolean;
  lastMessage: any;
  sendMessage: (msg: any) => void;
}

const BrowtrixContext = createContext<BrowtrixContextType | null>(null);

export function BrowtrixProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("Browtrix WS Connected");
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Received:", data);
        setLastMessage(data);
      } catch (e) {
        console.error("Failed to parse WS message:", event.data);
      }
    };

    ws.onclose = () => {
      console.log("Browtrix WS Closed. Reconnecting...");
      setIsConnected(false);
      wsRef.current = null;
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = (error) => {
      console.error("Browtrix WS Error:", error);
      ws.close();
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback((msg: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    } else {
      console.warn("Cannot send message, WS not connected");
    }
  }, []);

  return (
    <BrowtrixContext.Provider value={{ isConnected, lastMessage, sendMessage }}>
      {children}
    </BrowtrixContext.Provider>
  );
}

export function useBrowtrix() {
  const context = useContext(BrowtrixContext);
  if (!context) {
    throw new Error("useBrowtrix must be used within a BrowtrixProvider");
  }
  return context;
}
