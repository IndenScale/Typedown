"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    // Default to English
    router.replace("/en");
  }, [router]);

  return null;
}
