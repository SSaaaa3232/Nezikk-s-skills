---
name: docx-creater
description: Create, finish, and format `.docx` documents from user-provided content or drafted text. Use when the user asks to generate a Word document, export content to `.docx`, finish document formatting, or explicitly types `/docx-create`. Also use when the user wants common document-format requirements applied, such as title size, heading style, line spacing, numbering layout, italics, subscript, or Chinese/Western spacing.
---

# Docx Creater

## Overview

Create or update `.docx` documents in a repeatable way. Treat `/docx-create` as an explicit trigger to start the workflow.

Before writing or generating the document, ask the user to confirm the required formatting rules unless the requirements are already complete and unambiguous in the conversation.

## Workflow

1. Check whether the user already provided the document content.
If not, ask whether they want:
- content drafting first
- formatting only on existing content
- both drafting and formatting

2. Ask formatting questions before generating the `.docx`.
Do this before touching the final file unless the user has already specified everything needed.

Ask only the necessary items. Typical questions:
- title and subtitle rules
- heading levels and numbering style
- line spacing
- paragraph spacing and indentation
- font family and size for Chinese and Western text
- whether numbered items should have blank lines between them
- nomenclature rules such as protein roman, gene italics
- special typography such as subscript or superscript

3. Confirm output target.
Determine:
- output filename
- output directory
- whether to overwrite an existing `.docx`
- whether the user wants a new file or an update to an existing file

4. Prepare a neutral intermediate text source.
Use Markdown or another editable text form to structure the document before conversion.

5. Generate the `.docx`.
Prefer a stable converter already installed in the environment, such as `pandoc`, when available.
If document-wide formatting must be controlled, use a reference `.docx` template rather than relying on default export styles.

6. Apply format-sensitive details carefully.
Typical mappings:
- genes: italic
- proteins: roman/upright
- chemical stoichiometric numbers: subscript
- Chinese and Western mixed text: insert necessary spaces where style rules require them

7. Verify the output file.
Check that:
- the file exists
- the file is a valid `.docx`
- the filename matches the user request
- key formatting markers that were explicitly requested are present

8. Report what was done and any remaining uncertainty.
If some formatting points could not be guaranteed automatically, say so briefly and identify which ones need manual spot-checking in Word.

## Decision Rules

- If the user typed `/docx-create`, start by asking for or confirming formatting requirements.
- If the user already gave precise formatting rules, do not ask redundant questions.
- If the request is only to update a phrase or sentence inside an existing `.docx`, preserve the rest of the document structure.
- If the environment lacks a reliable `.docx` converter, say so and fall back to producing a clean intermediate source the user can convert later.

## Claude Compatibility

Keep this skill portable.

- Write workflow guidance in plain language, not platform-specific tool assumptions.
- Prefer describing capabilities like "generate a `.docx` with an installed converter" over hard-coding one assistant runtime.
- Use `/docx-create` and explicit phrases such as "generate a Word document" in the description so different assistants can discover the trigger.

This skill is intended to be callable from Claude as long as Claude is configured to discover skills from the same skill directory or from a copied copy of this folder.

## Output Standard

Default to concise, practical document generation.

- Preserve user terminology.
- Do not invent formatting requirements.
- Ask first when requirements are missing.
- Prefer deterministic formatting over decorative styling.
