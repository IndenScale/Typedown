from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionOptions,
    CompletionParams,
)

from typedown.server.application import server, TypedownLanguageServer
from typedown.server.services import CompletionService, CompletionContext


@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["["]))
def completions(ls: TypedownLanguageServer, params: CompletionParams):
    """LSP completion handler - delegates to CompletionService."""
    if not ls.is_ready:
        return []
    if not ls.compiler:
        return []
    
    # Get document content from workspace
    doc = ls.workspace.get_text_document(params.text_document.uri)
    
    # Create completion context
    context = CompletionContext(
        file_path=doc.path if hasattr(doc, 'path') else None,
        content=doc.source,
        line=params.position.line,
        character=params.position.character
    )
    
    # Delegate to service layer
    service = CompletionService(ls.compiler)
    return service.complete(context)
