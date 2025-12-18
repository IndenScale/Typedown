import * as path from "path";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  Executable,
  CloseAction,
  ErrorAction,
  State,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;
let outputChannel: vscode.OutputChannel;

export async function activate(context: vscode.ExtensionContext) {
  // Register restart command
  const restartCommand = vscode.commands.registerCommand(
    "typedown.restartLsp",
    async () => {
      if (client) {
        await client.restart();
      } else {
        await startServer(context);
      }
    }
  );

  context.subscriptions.push(restartCommand);

  await startServer(context);
}
async function startServer(context: vscode.ExtensionContext) {
  // Ensure we don't leak clients if startServer is called multiple times
  if (client) {
    // If client exists, trying to start a new one is weird without stopping old one.
    // But restartLsp command calls client.restart if client exists.
    // So startServer is only called if client is null.
    // However, for safety:
    try {
      await client.stop();
    } catch (e) {
      /* ignore */
    }
    client = undefined;
  }

  // Get config
  const config = vscode.workspace.getConfiguration("typedown");
  const command = config.get<string>("server.command") || "uv";
  const args = config.get<string[]>("server.args") || [
    "run",
    "--extra",
    "server",
    "td",
    "lsp",
  ];

  // Robust CWD detection: Use first workspace folder, or user home/current dir if no workspace
  let cwd = process.cwd();
  if (
    vscode.workspace.workspaceFolders &&
    vscode.workspace.workspaceFolders.length > 0
  ) {
    cwd = vscode.workspace.workspaceFolders[0].uri.fsPath;
  }

  // 1. Try to use local venv binary directly to bypass 'uv' wrappers
  // This avoids signal propagation issues (Stopping server timed out)
  // We search in the workspace root and parent directories (in case workspace is a subfolder)
  const fs = require("fs");
  let foundVenvBin = "";

  const searchPaths = [cwd, path.dirname(cwd), path.dirname(path.dirname(cwd))];

  for (const searchPath of searchPaths) {
    const potentialBin =
      process.platform === "win32"
        ? path.join(searchPath, ".venv", "Scripts", "td.exe")
        : path.join(searchPath, ".venv", "bin", "td");

    if (fs.existsSync(potentialBin)) {
      foundVenvBin = potentialBin;
      break;
    }
  }

  let finalCommand = command;
  let finalArgs = args;

  // Create output channel for debugging
  if (!outputChannel) {
    outputChannel = vscode.window.createOutputChannel("Typedown Client");
  }

  if (command === "uv" && foundVenvBin) {
    outputChannel.appendLine(`[Info] Using local venv binary: ${foundVenvBin}`);
    finalCommand = foundVenvBin;
    finalArgs = ["lsp"];
  } else {
    outputChannel.appendLine(
      `[Info] Using command: ${finalCommand} ${finalArgs.join(" ")}`
    );
  }

  const serverOptions: Executable = {
    command: finalCommand,
    args: finalArgs,
    options: {
      cwd: cwd,
      env: { ...process.env, TYPEDOWN_LSP_MODE: "1" },
    },
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [
      { scheme: "file", language: "markdown" },
      { scheme: "file", language: "typedown" }, // Also support .td
    ],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher("**/*.{md,td,py}"),
    },
    outputChannel: outputChannel, // Assign the output channel here
    traceOutputChannel: outputChannel,
  };

  client = new LanguageClient(
    "typedown",
    "Typedown Language Server",
    serverOptions,
    clientOptions
  );

  client.onDidChangeState((event) => {
    outputChannel.appendLine(
      `[Info] Client state change: ${event.oldState} -> ${event.newState}`
    );
  });

  // Start the client. This will also launch the server
  await client.start();
  outputChannel.appendLine("[Info] Typedown LSP Client Activated!");
}

export function deactivate(): Thenable<void> | undefined {
  if (outputChannel) {
    outputChannel.appendLine("[Info] Deactivate called.");
  }
  if (!client) {
    return undefined;
  }
  // Gracefully stop, suppressing "timed out" errors which are common with Python processes
  return client.stop().catch((err) => {
    console.warn("Typedown Client stop error (suppressed):", err);
  });
}
