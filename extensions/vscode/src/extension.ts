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
let statusBarItem: vscode.StatusBarItem;

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

  // Status Bar
  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100
  );
  statusBarItem.command = "typedown.restartLsp";
  context.subscriptions.push(statusBarItem);

  // Configuration Change Listener
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration(async (e) => {
      if (e.affectsConfiguration("typedown.server")) {
        const item = await vscode.window.showInformationMessage(
          "Typedown Server configuration changed. Restart server?",
          "Yes",
          "No"
        );
        if (item === "Yes") {
          vscode.commands.executeCommand("typedown.restartLsp");
        }
      }
    })
  );

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
    if (event.newState === State.Running) {
      statusBarItem.text = "$(check) Typedown";
      statusBarItem.tooltip = "Typedown Engine is Ready";
      statusBarItem.show();
    } else if (event.newState === State.Starting) {
      statusBarItem.text = "$(sync~spin) Typedown";
      statusBarItem.tooltip = "Starting Typedown Engine...";
      statusBarItem.show();
    } else {
      statusBarItem.text = "$(error) Typedown";
      statusBarItem.tooltip = "Typedown Engine Stopped";
      statusBarItem.show();
    }
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
