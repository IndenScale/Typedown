# Changelog

## [0.2.13] - 2026-01-05

### Changed

- **Strict Block Signatures**:
  - `model:<ID>`: ID must strictly match the Class Name defined in the block.
  - `spec:<ID>`: ID must strictly match a Function Name (`def <ID>`) defined in the block.
  - Entity IDs are now strictly validated (alphanumeric, dots, dashes, underscores).
- **Import Restrictions**:
  - **Models**: `model` blocks now throw an error if they contain `import` or `from` statements. All dependencies must be injected via `config.td` to ensure schema portability.
- **Parsing**:
  - Spec/Entity block headers are now whitespace-insensitive around the colon (e.g., `spec : id`).

### Added

- **Local Analysis Spec**: Support for `query()` injection in local spec execution context, enabling complex logic like `query(subject.manager)`.
