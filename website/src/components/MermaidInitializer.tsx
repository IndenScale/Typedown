"use client";

import { useEffect } from "react";
import mermaid from "mermaid";

export function MermaidInitializer() {
  useEffect(() => {
    // Initialize mermaid
    mermaid.initialize({
      startOnLoad: true,
      theme: "dark",
      securityLevel: "loose",
      fontFamily: "inherit",
    });
    
    // Manually trigger rendering
    mermaid.contentLoaded();
  }, []); // Run on mount

  return null;
}
