# Internal Data Model

The compiler maintains a structured representation of the documentation in memory.

## Document Node

Represents a Markdown file.

- `path`: File path
- `frontmatter`: Merged metadata
- `entities`: List of Entities defined within the file

## Entity Node

Represents a data object.

- `id`: Unique identifier
- `class_ref`: Pydantic class reference
- `raw_data`: Raw data in the source code block
- `resolved_data`: Complete data after desugaring
- `source_location`: Filename and line number (for error reporting)
