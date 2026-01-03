# Agent Skills as Code

This example demonstrates how to use Typedown to define **Agent Skills** (or Tools) with the same rigor you apply to your production code.

## The Problem

In most agentic frameworks (Swarm, LangChain, fastai), Skills are defined in either:

1. **Raw Markdown/YAML**: Flexible but error-prone. One typo in `properties` breaks the JSON schema.
2. **Code (Python/TS)**: Hard to read for non-engineers, and hard to version control independently of the implementation.

## The Solution: Typedown Skills

By defining Skills as **Typedown Entities**, you get:

1.  **Strict Schema Validation**: You cannot define a Skill that violates the `Skill` model (defined in `meta/skill_schema.td`).
2.  **Business Logic Checks**: The `spec` block in `definition.td` automatically validates best practices (e.g., "All parameters must have descriptions").
3.  **LSP Support**: Autocomplete works when writing prompts / examples.

## File Structure

- **[meta/skill_schema.td](./meta/skill_schema.td)**: The "Metamodel". Defines what a Skill _is_. Use this to enforce company-wide standards (e.g., "All skills must have an 'author' field").
- **[skills/browser_mock/definition.td](./skills/browser_mock/definition.td)**: An instance of a Skill. This is the source of truth.

## Workflow

1.  **Write** the skill definition in `.td`.
2.  **Validate** it using `td check` or the VS Code extension.
3.  **Compile** it (conceptually) into the format your LLM needs:
    - _Export to JSON Schema_ for OpenAI Function Calling.
    - _Export to Prompt Markdown_ for Claude System Prompts.

```bash
# Verify your skills meet the quality bar
uvx typedown check examples/02_agent_skills
```
