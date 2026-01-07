"use client";

import { PlaygroundHeader } from "@/components/playground/PlaygroundHeader";
import { FileExplorer } from "@/components/playground/FileExplorer";
import { PlaygroundEditor } from "@/components/playground/PlaygroundEditor";
import { usePlaygroundStore } from "@/store/usePlaygroundStore";
import { useEffect } from "react";
import { Dictionary } from "@/dictionaries/types";
import { TranslationProvider } from "@/components/playground/TranslationContext";

export function PlaygroundClient({
  lang,
  dictionary,
}: {
  lang: string;
  dictionary: Dictionary["playground"];
}) {
  const setLang = usePlaygroundStore((state) => state.setLang);

  useEffect(() => {
    if (lang) {
      setLang(lang);
    }
  }, [lang, setLang]);

  return (
    <TranslationProvider value={dictionary}>
      <div className="flex h-screen w-full flex-col bg-background text-foreground overflow-hidden">
        <PlaygroundHeader />

        <div className="flex flex-1 overflow-hidden">
          <FileExplorer />

          <main className="flex-1 relative bg-white dark:bg-[#0A0A0A]">
            <PlaygroundEditor />
          </main>
        </div>
      </div>
    </TranslationProvider>
  );
}
