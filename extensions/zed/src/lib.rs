use zed_extension_api::{Command, Extension, LanguageServerId, Worktree};

struct TypedownExtension;

impl Extension for TypedownExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &LanguageServerId,
        _worktree: &Worktree,
    ) -> zed_extension_api::Result<Command> {
        Ok(Command {
            command: "/Users/indenscale/Documents/Projects/Monoco/Typedown/.venv/bin/typedown".to_string(),
            args: vec!["lsp".to_string()],
            env: vec![],
        })
    }
}

zed_extension_api::register_extension!(TypedownExtension);
