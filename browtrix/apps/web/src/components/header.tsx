"use client";
import Link from "next/link";
import { ModeToggle } from "./mode-toggle";
import { useBrowtrix } from "@/lib/browtrix-context";

export default function Header() {
	const { isConnected } = useBrowtrix();
	const links = [{ to: "/", label: "Home" }] as const;

	return (
		<div>
			<div className="flex flex-row items-center justify-between px-2 py-1">
				<nav className="flex gap-4 text-lg">
					{links.map(({ to, label }) => {
						return (
							<Link key={to} href={to}>
								{label}
							</Link>
						);
					})}
				</nav>
				<div className="flex items-center gap-2">
					<div className="flex items-center gap-2 mr-4">
						<div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`} />
						<span className="text-xs text-muted-foreground">
							{isConnected ? "Connected" : "Disconnected"}
						</span>
					</div>
					<ModeToggle />
				</div>
			</div>
			<hr />
		</div>
	);
}
