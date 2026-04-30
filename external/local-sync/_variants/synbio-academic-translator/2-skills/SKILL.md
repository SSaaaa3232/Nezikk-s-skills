---
name: synbio-academic-translator
description: Use when the user enters /translate or asks for Chinese-to-English translation, polishing, or terminology normalization for academic writing in synthetic biology, metabolic engineering, molecular biology, microbial engineering, or related bioscience papers.
---

# SynBio Academic Translator

## Overview

This skill translates Chinese academic text into publication-ready English for synthetic biology and adjacent bioscience fields.

Default mode:
- faithful translation first
- journal-style rewriting second
- terminology normalization throughout

Default writing target:
- engineering-oriented synthetic biology journal style
- precise, compact, technically explicit
- strong on construct design, regulatory logic, pathway engineering, and experimental claims

## When to Use

Use this skill when:
- the user explicitly types `/translate`
- the user wants Chinese academic text translated into English
- the user wants translation plus polishing
- the user wants terminology unified for synthetic biology or bioscience writing
- the input is a title, abstract, introduction, results, methods, discussion, figure legend, or response-to-reviewers text

Do not use this skill to:
- invent missing data
- expand conclusions beyond the source text
- generate a literature review from scratch
- act as a fact checker unless the user separately asks for verification

## Input Handling

If the user provides `/translate` with text, process it directly.

If the user provides `/translate` with a `.docx` file path, extract the Chinese paragraphs from the document before translating.

For `.docx` input:
- prefer the bundled script `scripts/extract_docx_paragraphs.py`
- preserve paragraph order
- skip empty paragraphs
- skip clearly English-only title lines when the user asked to translate the Chinese body text
- if the document mixes headings and body text, keep section headings such as `引言` when they help structure the translation

If the user provides only `/translate`, ask for:
- the Chinese source text or a `.docx` path
- optional section type if the text is ambiguous

Infer the section type when possible:
- title
- abstract
- introduction
- results
- methods
- discussion
- figure legend

If the section type is unclear and wording depends on it, ask one short clarifying question.

## Workflow

Follow this sequence:

1. Identify the section type and rhetorical goal.
2. If the input is a `.docx`, extract the source paragraphs first.
3. Translate faithfully, preserving the original logic and claim strength.
4. Rewrite into concise academic English suited to synthetic biology and engineering papers.
5. Normalize terminology and expression level across the passage.
6. Flag ambiguous source wording with `Need Author Check`.

## Style Rules

- Prefer precise technical English over literal sentence-by-sentence translation.
- Keep causal strength aligned with the source. Do not turn correlation into mechanism.
- Prefer compact and direct phrasing over Chinese-influenced clause stacking.
- Use consistent terminology within the same passage.
- Preserve quantitative values, units, strain names, plasmid names, gene names, and experimental conditions exactly as given.
- For methods, prioritize reproducibility and procedural clarity.
- For results, prioritize observation, comparison, and evidence wording.
- For discussion, prioritize interpretation without overstating certainty.

## Output Contract

Default output has exactly three sections in this order.

### Final Translation

Provide the final English text only. It should read like manuscript-ready prose, not annotated translation.

### Terminology Map

List only the terms that appear in the current passage, using this structure:

`Chinese term | Standard English term | Note`

Use the canonical terms from `references/terminology.md` unless the local context clearly requires a different standard term.

### Revision Notes

Briefly explain only the high-value edits:
- terminology normalization
- major syntactic restructuring
- logic or cohesion improvements
- places marked `Need Author Check`

Do not provide line-by-line commentary unless the user asks for it.

## Translation Priorities by Section

### Title
- optimize for precision and scope
- avoid unnecessary articles and filler words

### Abstract
- preserve objective, method, result, and conclusion order
- keep claims compact and publication-ready

### Introduction
- improve logical transitions
- avoid repetitive motivation statements

### Results
- foreground observations and comparisons
- avoid overclaiming mechanism

### Methods
- keep terms standardized and operations reproducible
- prefer unambiguous procedural language

### Discussion
- separate interpretation from proof
- preserve hedging where the source is cautious

### Figure Legend
- keep concise, descriptive, and data-linked

## Guardrails

- Never add references, datasets, mechanisms, or experimental details not present in the source.
- Never silently strengthen novelty, significance, or universality claims.
- If a Chinese term is underspecified, choose the safest standard rendering and mark it in `Revision Notes`.
- If multiple English renderings are possible, prefer the one most consistent with synthetic biology and molecular bioscience literature.

## Domain Preference

Assume the paper may involve:
- synthetic biology
- metabolic engineering
- microbial cell factories
- filamentous fungi or yeast engineering
- pathway design
- heterologous expression
- promoter or regulatory element engineering

Load `references/terminology.md` whenever terminology consistency materially affects the output.

If the user works from manuscript files instead of pasted text, also use `scripts/extract_docx_paragraphs.py` for `.docx` sources before translation.
