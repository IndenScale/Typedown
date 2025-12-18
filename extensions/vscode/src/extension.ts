import * as path from "path";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  Executable,
} from "vscode-languageclient/node";

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
  // Register restart command
  const restartCommand = vscode.commands.registerCommand(
    "typedown.restartLsp",
    () => {
      if (client) {
        return client.restart();
      } else {
        startServer(context);
      }
    }
  );

  context.subscriptions.push(restartCommand);

  startServer(context);
}

function startServer(context: vscode.ExtensionContext) {
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

  const serverOptions: Executable = {
    command: command,
    args: args,
    options: {
      cwd: cwd,
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
  };

  client = new LanguageClient(
    "typedown",
    "Typedown Language Server",
    serverOptions,
    clientOptions
  );

  client.start();

  vscode.window.showInformationMessage("Typedown LSP Client Activated!");
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}
