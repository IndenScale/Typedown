"use client";

import { usePlaygroundStore } from "@/store/usePlaygroundStore";
import { FileCode, FileJson, FileType } from "lucide-react";
import { clsx } from "clsx";

function getFileIcon(fileName: string) {
  if (fileName.endsWith(".td"))
    return <FileCode size={14} className="text-success" />;
  if (fileName.endsWith(".py"))
    return <FileCode size={14} className="text-blue-400" />;
  if (fileName.endsWith(".md"))
    return <FileType size={14} className="text-gray-400" />;
  return <FileCode size={14} />;
}

export function FileExplorer() {
  const {
    files: filesRecord,
    activeFileName,
    openFile: selectFile,
  } = usePlaygroundStore();
  const files = Object.values(filesRecord);

  return (
    <div className="flex flex-col w-64 border-r border-black/5 dark:border-white/5 bg-gray-50/50 dark:bg-[#0A0A0A]">
      <div className="p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">
        Explorer
      </div>
      <div className="flex-1 overflow-y-auto">
        {files.map((file) => (
          <button
            key={file.name}
            onClick={() => selectFile(file.name)}
            className={clsx(
              "w-full flex items-center gap-2 px-4 py-2 text-sm text-left transition-colors border-l-2",
              activeFileName === file.name
                ? "bg-white dark:bg-white/5 border-success text-foreground font-medium"
                : "border-transparent text-gray-500 hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5"
            )}>
            {getFileIcon(file.name)}
            <span className="truncate">{file.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
