"use client";

import { createContext, useContext, ReactNode } from "react";
import { Dictionary } from "@/dictionaries/types";

const TranslationContext = createContext<Dictionary["playground"] | null>(null);

export function TranslationProvider({
  children,
  value,
}: {
  children: ReactNode;
  value: Dictionary["playground"];
}) {
  return (
    <TranslationContext.Provider value={value}>
      {children}
    </TranslationContext.Provider>
  );
}

export function useTranslation() {
  const context = useContext(TranslationContext);
  if (!context) {
    throw new Error("useTranslation must be used within a TranslationProvider");
  }
  return context;
}
