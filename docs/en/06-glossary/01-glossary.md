---
title: Glossary
---

# Glossary

This document summarizes core terms and definitions in the Typedown ecosystem.

## 1. Structure & Validation

### Model

- **Block Signature**: ` ```model:<Type> ``` `
- **Definition**: A blueprint for data structure, corresponding to a Pydantic class. It is the template for all entities, defining the shape (Schema) and intrinsic logic of the data.

### Entity

- **Block Signature**: ` ```entity <Type>: <ID> ``` `
- **Definition**: The basic data unit in Typedown. It is a concrete instance of a Model, containing YAML data that conforms to the Schema definition.

### Spec

- **Block Signature**: ` ```spec:<ID> ``` `
- **Definition**: Test cases written based on Pytest, used to describe complex logical constraints that require access to the **global symbol table**. Specs are bound to Entities via `tags` to verify the consistency of the entity within the entire knowledge graph.

### Model Schema

The specification defining the data shape. It stipulates which fields an entity must contain and the types of those fields.

### Model Validator

Validation logic defined within the Model Schema, used to ensure the integrity of single data items (independent of external context).

- **Field Validator**: Validation for individual field values (e.g., email format check).
- **Model Validator**: Joint validation across multiple fields of a model instance (e.g., `end_time` must be later than `start_time`).

### Oracle

_(Not yet implemented)_ Sources of information external to the Typedown system that provide trusted statements (e.g., ERP, government data APIs). They serve as reference frames for truth, used to verify consistency between document content and the real world.

## 2. Identifiers & References

### Reference

The act of pointing to another entity using `[[target]]` syntax within documentation. References are the foundation for building the Knowledge Graph.

### ID

The name of an entity. IDs are unique within their scope and are used to reference entities.

- **Format**: Any string that doesn't start with `sha256:`.
- **Examples**: `alice`, `user-alice-v1`, `users/alice`

### Content Hash

A SHA-256 hash computed from the entity's content, used for content addressing.

- **Format**: `sha256:` prefix + 64-character hexadecimal string.
- **Usage**: Immutable references, version locking, history tracking.

### Slug

A URL-friendly string identifier format, typically used as an ID.

## 3. Runtime & Scoping

### Context

The set of symbols visible when parsing a specific file, including available Models, IDs, and Variables.

### Scope

The visibility range of symbols. Typedown uses Lexical Scoping, with the following hierarchy:

1. **Local Scope**: Current file.
2. **Directory Scope**: Current directory (defined by `config.td`).
3. **Parent Scopes**: Recursive parent directories.
4. **Global Scope**: Project global configuration (`typedown.yaml`).

### Config Block

- **Block Signature**: ` ```config python ``` `
- **Definition**: A code block used to dynamically configure the compilation context, usually only allowed in `config.td` files. Used to import Schemas, define global variables, or register scripts.

### Environment Overlay

Achieved by defining `config.td` at different directory levels to modify or override the context of lower-level directories. This allows the same set of documentation code to exhibit different behaviors in different environments (e.g., Production vs Staging).

## 4. Toolchain

### Compiler

The core engine of Typedown, responsible for parsing Markdown, executing Python code, building symbol tables, and running validation logic.

### LSP (Language Server Protocol)

Typedown's implementation of the editor service protocol, providing features like code completion, jump to definition, and real-time diagnostics for editors like VS Code.

### Doc Lens

A visual aid tool in the IDE used to display context information of the current code block in real-time (e.g., inherited configurations, resolved reference targets), helping developers visualize context state.
