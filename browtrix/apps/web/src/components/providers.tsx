"use client";

import { BrowtrixOverlay } from "@/components/browtrix-overlay";
import { BrowtrixProvider } from "@/lib/browtrix-context";
import { ThemeProvider } from "./theme-provider";
import { Toaster } from "./ui/sonner";

export default function Providers({ children }: { children: React.ReactNode }) {
	return (
		<ThemeProvider
			attribute="class"
			defaultTheme="system"
			enableSystem
			disableTransitionOnChange
		>
			<BrowtrixProvider>
				{children}
				<BrowtrixOverlay />
				<Toaster richColors />
			</BrowtrixProvider>
		</ThemeProvider>
	);
}
