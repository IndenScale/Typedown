"use client";

import { useLSPClient } from "@/hooks/useLSPClient";
import { usePlaygroundStore } from "@/store/usePlaygroundStore";
import React, { useEffect } from "react";

// Memoized to prevent re-renders from parent re-renders
export const GlobalLSPManager = React.memo(function GlobalLSPManager() {
  // This component simply invokes the hook to ensure global singleton initialization.
  // It renders nothing.
  useLSPClient();

  const hydrateDemos = usePlaygroundStore((state) => state.hydrateDemos);

  useEffect(() => {
    hydrateDemos();
  }, [hydrateDemos]);

  return null;
});
