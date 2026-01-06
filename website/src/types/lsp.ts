export interface TypedownSyncFileParams {
  textDocument: {
    uri: string;
    languageId?: string;
    version?: number;
    text: string;
  };
}

export interface TypedownSyncFileMessage {
  jsonrpc: "2.0";
  method: "typedown/syncFile" | "textDocument/didOpen";
  params: TypedownSyncFileParams;
}

export interface TypedownResetFileSystemMessage {
  jsonrpc: "2.0";
  method: "typedown/resetFileSystem";
  params?: Record<string, never>;
}

export type TypedownWorkerMessage =
  | TypedownSyncFileMessage
  | TypedownResetFileSystemMessage;
