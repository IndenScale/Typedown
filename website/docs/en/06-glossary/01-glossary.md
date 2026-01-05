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
- **Block Signature**: ` ```entity <Type>: <Identifier> ``` `
- **Definition**: The basic data unit in Typedown. It is a concrete instance of a Model, containing YAML data that conforms to the Schema definition.

### Spec
- **Block Signature**: ` ```spec:<Identifier> ``` `
- **Definition**: Test cases written based on Pytest, used to describe complex logical constraints that require access to the **global symbol table**. Specs are bound to Entities via `tags` to verify the consistency of the entity within the entire knowledge graph.

### Model Schema
The specification defining the data shape. It stipulates which fields an entity must contain and the types of those fields.

### Model Validator
Validation logic defined within the Model Schema, used to ensure the integrity of single data items (independent of external context).
- **Field Validator**: Validation for individual field values (e.g., email format check).
- **Model Validator**: Joint validation across multiple fields of a model instance (e.g., `end_time` must be later than `start_time`).

### Oracle
*(Not yet implemented)* Sources of information external to the Typedown system that provide trusted statements (e.g., ERP, government data APIs). They serve as reference frames for truth, used to verify consistency between document content and the real world.

## 2. Identifiers & References

### Reference
The act of pointing to another entity using `[[target]]` syntax within documentation. References are the foundation for building the Knowledge Graph.

### System ID
**L1 Identifier**. The globally unique name of an entity, usually reflecting its location in the file system or logical path. Used for version control and persistent references.

### Handle
**L2 Identifier**. An alias used within a specific Scope. Used for Dependency Injection (DI) and polymorphic configuration, allowing the same name to point to different entities in different environments.

### Slug
A URL-friendly string identifier format, typically used as a System ID.

### Triple Resolution
The lookup mechanism used by the compiler when resolving references, with priority from high to low:
1. **L0: Content Hash**: Immutable addressing based on content (e.g., `sha256:...`).
2. **L1: System ID**: Globally unique, versioned identifier (e.g., `infra/db-prod-v1`).
3. **L2: Handle**: Context-dependent, mutable name (e.g., `db_primary`).

## 3. Runtime & Scoping

### Context
The set of symbols visible when parsing a specific file, including available Models, Handles, and Variables.

### Scope
The visibility range of symbols. Typedown uses Lexical Scoping, with the following hierarchy:
1. **Local Scope**: Current file.
2. **Directory Scope**: Current directory (defined by `config.td`).
3. **Parent Scopes**: Recursive parent directories.
4. **Global Scope**: Project global configuration (`typedown.yaml`).

### Config Block
- **Block Signature**: ` ```config:python ``` `
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
