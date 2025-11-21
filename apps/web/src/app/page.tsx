"use client";

import { DottedGlowBackground } from "@/components/overlay/dotted-glow-background";
import { TextHoverEffect } from "@/components/text-effects/text-hover-effect";
import { ModeToggle } from "@/components/theme/mode-toggle";
import { useBrowtrix } from "@/lib/contexts/browtrix-context";

export default function Home() {
	const { isConnected } = useBrowtrix();

	return (
		<div className="h-screen flex items-center justify-center relative">
			<DottedGlowBackground
				className="pointer-events-none mask-radial-to-90% mask-radial-at-center"
				opacity={0.4}
				gap={12}
				radius={2}
				colorLightVar="--color-neutral-500"
				glowColorLightVar="--color-neutral-600"
				colorDarkVar="--color-neutral-500"
				glowColorDarkVar="--color-sky-800"
				backgroundOpacity={1}
				speedMin={0.4}
				speedMax={0.8}
				speedScale={0.5}
			/>
			<TextHoverEffect text="BROWTRIX" />
			<div className="fixed top-4 left-4">
				<div
					className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"} animate-pulse`}
				/>
			</div>
			<div className="fixed bottom-4 right-4">
				<ModeToggle />
			</div>
		</div>
	);
}
