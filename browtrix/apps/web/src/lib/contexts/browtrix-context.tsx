"use client";

import type React from "react";
import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useRef,
	useState,
} from "react";

interface BrowtrixMessage {
	type: string;
	id: string;
	params?: Record<string, unknown>;
	message?: string;
	title?: string;
	timeout?: number;
	validation?: string;
}

interface BrowtrixResponse {
	id: string;
	success: boolean;
	approved?: boolean;
	button_clicked?: string;
	timeout_occurred?: boolean;
	value?: string;
	user_input?: string;
	input_type?: string;
	validation_passed?: boolean;
	error?: string;
	html_content?: string;
	url?: string;
	title?: string;
	timestamp: number;
	execution_time_ms?: number;
	metadata?: Record<string, unknown>;
}

interface BrowtrixContextType {
	isConnected: boolean;
	lastMessage: BrowtrixMessage | null;
	sendMessage: (msg: BrowtrixResponse) => void;
}

const BrowtrixContext = createContext<BrowtrixContextType | null>(null);

export function BrowtrixProvider({ children }: { children: React.ReactNode }) {
	const [isConnected, setIsConnected] = useState(false);
	const [lastMessage, setLastMessage] = useState<BrowtrixMessage | null>(null);
	const wsRef = useRef<WebSocket | null>(null);
	const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

	const connect = useCallback(() => {
		const WS_URL = (process.env.NEXT_PUBLIC_BROWTRIX_MCP_WS_URL) as string;
		const ws = new WebSocket(WS_URL);

		ws.onopen = () => {
			console.log("Browtrix WS Connected");
			setIsConnected(true);
		};

		ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);
				console.log("Received:", data);
				console.log("Message type:", data.type);
				console.log("Message ID:", data.id);
				setLastMessage(data);
			} catch (_e) {
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

	const sendMessage = useCallback((msg: BrowtrixResponse) => {
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
