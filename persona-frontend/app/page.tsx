"use client";

import { useState } from "react";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { ChatInterface } from "@/components/ChatInterface";
import { IntroOverlay } from "@/components/IntroOverlay";
import { AnimatePresence } from "framer-motion";

export default function Home() {
  const [showIntro, setShowIntro] = useState(true);

  return (
    <main className="relative min-h-screen w-full overflow-hidden text-foreground">
      <AnimatedBackground />
      
      <AnimatePresence mode="wait">
        {showIntro ? (
          <IntroOverlay key="intro" onComplete={() => setShowIntro(false)} />
        ) : (
          <ChatInterface key="chat" />
        )}
      </AnimatePresence>
    </main>
  );
}
