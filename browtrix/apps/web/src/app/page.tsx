"use client";

import { useBrowtrix } from "@/lib/browtrix-context";

const TITLE_TEXT = `░▒▓███████▓▒░░▒▓███████▓▒░ ░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓███████▓▒░░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓███████▓▒░░▒▓█▓▒░░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓███████▓▒░ ░▒▓█████████████▓▒░   ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
                                                                                                           
                                                                                                           `;

export default function Home() {
	const { isConnected } = useBrowtrix();

	return (
		<div className="container mx-auto max-w-3xl px-4 py-2">
			<pre className="overflow-x-auto font-mono text-sm">{TITLE_TEXT}</pre>
			<div className="grid gap-6">
				<section className="rounded-lg border p-4">
					<h2 className="mb-2 font-medium">API Status</h2>
					<div className="flex items-center gap-2">
						<div className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`} />
						<span className="text-sm">
							{isConnected ? "Connected to Browtrix Server" : "Disconnected from Browtrix Server"}
						</span>
					</div>
				</section>

				<section className="rounded-lg border p-4">
					<h2 className="mb-2 font-medium">Welcome to Browtrix</h2>
					<p className="text-sm text-muted-foreground mb-4">
						This web application connects to the Browtrix MCP server via WebSocket to provide browser automation capabilities.
					</p>
					<div className="space-y-2 text-sm">
						<p><strong>Available Tools:</strong></p>
						<ul className="list-disc list-inside space-y-1 text-muted-foreground">
							<li>HTML Snapshot - Capture the current page content</li>
							<li>Confirmation Alert - Show confirmation dialogs</li>
							<li>Question Popup - Collect user input</li>
						</ul>
					</div>
				</section>

				<section className="rounded-lg border p-4">
					<h2 className="mb-2 font-medium">Test Content</h2>
					<p className="text-sm text-muted-foreground">
						This is sample content to test the HTML snapshot functionality. The snapshot tool will capture this entire page
						and return the HTML content to the MCP client.
					</p>
					<div className="mt-4 p-3 bg-muted rounded-md">
						<h3 className="font-medium mb-2">Sample Section</h3>
						<p className="text-sm">
							Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
						</p>
					</div>
				</section>
			</div>
		</div>
	);
}
