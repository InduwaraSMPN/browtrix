"use client";

import { useBrowtrix } from "@/lib/browtrix-context";
import { TextHoverEffect } from "@/components/ui/text-hover-effect";
import { ModeToggle } from "@/components/mode-toggle";
import { RipplePulseLoader } from "@/components/ui/ripple-pulse-loader";

export default function Home() {
  const { isConnected } = useBrowtrix();

  return (
    <div className="h-screen flex items-center justify-center relative">
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