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
import { useBrowtrix } from "@/lib/contexts/browtrix-context";
import { captureSnapshot } from "@/lib/utils/snapshot";

interface RequestState {
	id: string;
	type: "SHOW_CONFIRM" | "SHOW_INPUT";
	msg: string;
	validation?: string;
}

export function BrowtrixOverlay() {
	const { lastMessage, sendMessage } = useBrowtrix();
	const [activeRequest, setActiveRequest] = useState<RequestState | null>(null);
	const [inputValue, setInputValue] = useState("");
	const [error, setError] = useState("");

	useEffect(() => {
		if (!lastMessage) return;
		const { type, id, params, message, title, timeout, validation } =
			lastMessage;

		// Ensure required properties are present
		if (!type || !id) return;

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
			const msg: string =
				(params?.message as string) || message || "Confirm this action";
			console.log("Showing confirmation:", msg);
			setActiveRequest({ id, type, msg });
		} else if (type === "SHOW_INPUT") {
			// Handle both params format and direct fields
			const msg: string =
				(params?.message as string) || message || "Please enter your input";
			const valid: string =
				(params?.validation as string) || validation || "any";
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
		<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
			<Card className="w-full max-w-md mx-4 bg-white/95 dark:bg-gray-900/95 border-gray-200 dark:border-gray-800/50 shadow-2xl shadow-gray-200/50 dark:shadow-sky-900/20">
				<CardHeader>
					<CardTitle className="text-gray-900 dark:text-gray-100">
						{activeRequest.type === "SHOW_CONFIRM"
							? "Confirmation Request"
							: "Input Request"}
					</CardTitle>
				</CardHeader>
				<CardContent>
					<p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
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
								className="bg-gray-50 dark:bg-gray-800/50 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus-visible:border-sky-600 focus-visible:ring-sky-600/30"
							/>
							{error && (
								<p className="text-red-500 dark:text-red-400 text-xs mt-1">
									{error}
								</p>
							)}
						</form>
					)}
				</CardContent>
				<CardFooter className="flex justify-end gap-2">
					{activeRequest.type === "SHOW_CONFIRM" ? (
						<>
							<Button
								variant="outline"
								onClick={() => handleConfirm(false)}
								className="bg-gray-50 dark:bg-gray-800/50 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 hover:border-gray-400 dark:hover:border-gray-600"
							>
								No
							</Button>
							<Button
								onClick={() => handleConfirm(true)}
								className="bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-white shadow-lg shadow-gray-900/20 dark:shadow-gray-900/30"
							>
								Yes
							</Button>
						</>
					) : (
						<>
							<Button
								variant="outline"
								onClick={() => setActiveRequest(null)}
								className="bg-gray-50 dark:bg-gray-800/50 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 hover:border-gray-400 dark:hover:border-gray-600"
							>
								Cancel
							</Button>
							<Button
								type="submit"
								form="browtrix-form"
								className="bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-white shadow-lg shadow-gray-900/20 dark:shadow-gray-900/30"
							>
								Submit
							</Button>
						</>
					)}
				</CardFooter>
			</Card>
		</div>
	);
}
