"use client";

import { usePlaygroundStore } from "@/store/usePlaygroundStore";
import { Activity, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import clsx from "clsx";

type StatusConfig = {
  icon: React.ComponentType<{ className?: string }>;
  text: string;
  color: string;
  bgColor: string;
  iconColor: string;
  animate?: boolean;
};

export function LSPStatusIndicator() {
  const lspStatus = usePlaygroundStore((state) => state.lspStatus);

  const statusConfig: Record<typeof lspStatus, StatusConfig> = {
    disabled: {
      icon: Activity,
      text: "LSP Disabled",
      color: "text-gray-400",
      bgColor: "bg-gray-100 dark:bg-gray-800",
      iconColor: "text-gray-400",
    },
    connecting: {
      icon: Loader2,
      text: "Connecting...",
      color: "text-yellow-600 dark:text-yellow-500",
      bgColor: "bg-yellow-50 dark:bg-yellow-900/20",
      iconColor: "text-yellow-600 dark:text-yellow-500",
      animate: true,
    },
    connected: {
      icon: CheckCircle2,
      text: "LSP Ready",
      color: "text-green-600 dark:text-green-500",
      bgColor: "bg-green-50 dark:bg-green-900/20",
      iconColor: "text-green-600 dark:text-green-500",
    },
    error: {
      icon: AlertCircle,
      text: "LSP Error",
      color: "text-red-600 dark:text-red-500",
      bgColor: "bg-red-50 dark:bg-red-900/20",
      iconColor: "text-red-600 dark:text-red-500",
    },
  };

  const config = statusConfig[lspStatus];
  const Icon = config.icon;

  return (
    <div
      className={clsx(
        "flex items-center gap-2 px-2.5 py-1 rounded text-xs font-medium transition-all",
        config.bgColor,
        config.color
      )}
      title={`Language Server Status: ${config.text}`}>
      <Icon
        className={clsx(
          "w-3 h-3",
          config.iconColor,
          config.animate && "animate-spin"
        )}
      />
      <span className="text-[11px]">{config.text}</span>
    </div>
  );
}
