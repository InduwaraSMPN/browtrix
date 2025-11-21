"use client";

import { BrowtrixOverlay } from "@/components/overlay/browtrix-overlay";
import { ThemeProvider } from "@/components/theme/theme-provider";
import { Toaster } from "@/components/ui/sonner";
import { BrowtrixProvider } from "@/lib/contexts/browtrix-context";

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
