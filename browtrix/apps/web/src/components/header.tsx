"use client";
import Link from "next/link";

export default function Header() {
	const links = [] as const;

	return (
		<div>
			<div className="container mx-auto max-w-3xl px-4">
				<div className="flex flex-row items-center justify-between py-1">
					<nav className="flex gap-4 text-lg">
						{links.map(({ to, label }) => {
							return (
								<Link key={to} href={to}>
									{label}
								</Link>
							);
						})}
					</nav>
				</div>
			</div>
		</div>
	);
}
