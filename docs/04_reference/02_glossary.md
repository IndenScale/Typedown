---
title: Glossary
---

# Glossary

## Structure and Validation

### Model
- **Signature**: `model:<Type>`
- **Definition**: Data structure blueprint, corresponding to Pydantic class

### Entity
- **Signature**: `entity <Type>: <ID>`
- **Definition**: Typedown basic data unit, concrete instance of Model

### Spec
- **Signature**: `spec:<ID>`
- **Definition**: Pytest-based test case, validates global constraints

### Oracle
- **Definition**: External trusted information source (e.g., ERP, government interfaces), used to verify consistency between documents and reality

## Identifiers and References

### Ref (Reference)
The act of pointing to another entity using `[[target]]` syntax

### ID (Identifier)
Globally unique name of an entity, used for version control and precise referencing

## Runtime and Scope

### Context
The set of symbols visible when parsing a file

### Scope
Symbol visibility range, using lexical scoping:
1. Local Scope: Current file
2. Directory Scope: Current directory
3. Parent Scopes: Parent directory recursion
4. Global Scope: Project global

### Config Block
- **Signature**: `config python`
- **Definition**: Code block that configures the compilation context

## Toolchain

### Compiler
Core engine that parses Markdown, executes Python, and builds symbol tables

### LSP (Language Server Protocol)
Protocol implementation providing editors with completion, navigation, diagnostics, and other features

### Doc Lens
Visual tool in IDE that displays code block context information
