"use client";

import dynamic from "next/dynamic";
import React from "react";

const GlobalLSPManager = dynamic(
  () =>
    import("@/components/playground/GlobalLSPManager").then(
      (mod) => mod.GlobalLSPManager
    ),
  { ssr: false }
);

export function LSPClientWrapper() {
  return <GlobalLSPManager />;
}
