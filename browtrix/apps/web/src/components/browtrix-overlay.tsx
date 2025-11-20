"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useBrowtrix } from "@/lib/browtrix-context";
import { captureSnapshot } from "@/lib/snapshot";

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
		const { type, id, params, message, title, timeout, validation } =
			lastMessage;

		console.log("Received message:", {
			type,
			id,
			params,
			message,
			title,
			timeout,
			validation,
		});

		if (type === "GET_SNAPSHOT") {
			// Handle snapshot immediately without UI
			try {
				const content = captureSnapshot();
				sendMessage({
					id: id,
					success: true,
					html_content: content,
					url: window.location.href,
					title: document.title,
					timestamp: Date.now(),
					execution_time_ms: 50,
					metadata: {
						content_size: content.length,
						full_page: params?.full_page || true,
					},
				});
			} catch (_e) {
				sendMessage({
					id: id,
					success: false,
					error: "Failed to capture snapshot",
					timestamp: Date.now(),
				});
			}
		} else if (type === "SHOW_CONFIRM") {
			// Handle both params format and direct fields
			const msg = params?.message || message || "Confirm this action";
			console.log("Showing confirmation:", msg);
			setActiveRequest({ id, type, msg });
		} else if (type === "SHOW_INPUT") {
			// Handle both params format and direct fields
			const msg = params?.message || message || "Please enter your input";
			const valid = params?.validation || validation || "any";
			console.log("Showing input:", msg, "validation:", valid);
			setActiveRequest({
				id,
				type,
				msg,
				validation: valid,
			});
			setInputValue("");
			setError("");
		} else if (type === "ABORT_UI") {
			setActiveRequest((prev) => (prev && prev.id === id ? null : prev));
		}
	}, [lastMessage, sendMessage]);

	const handleConfirm = (approved: boolean) => {
		if (!activeRequest) return;
		console.log("Sending confirmation response:", {
			approved,
			id: activeRequest.id,
		});
		sendMessage({
			id: activeRequest.id,
			success: true,
			approved,
			button_clicked: approved ? "ok" : "cancel",
			timeout_occurred: false,
			timestamp: Date.now(),
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

		console.log("Sending input response:", {
			value: inputValue,
			id: activeRequest.id,
		});
		sendMessage({
			id: activeRequest.id,
			success: true,
			value: inputValue,
			user_input: inputValue, // Keep for compatibility
			input_type: "text",
			validation_passed: true,
			timestamp: Date.now(),
		});
		setActiveRequest(null);
	};

	if (!activeRequest) return null;

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
			<Card className="w-full max-w-md mx-4">
				<CardHeader>
					<CardTitle>
						{activeRequest.type === "SHOW_CONFIRM"
							? "Confirmation Request"
							: "Input Request"}
					</CardTitle>
				</CardHeader>
				<CardContent>
					<p className="text-sm text-muted-foreground mb-4">
						{activeRequest.msg}
					</p>

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
								No
							</Button>
							<Button onClick={() => handleConfirm(true)}>Yes</Button>
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
