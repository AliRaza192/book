<!-- SYNC IMPACT REPORT
Version change: N/A (initial constitution) → 1.0.0
List of modified principles: N/A (new constitution)
Added sections: All principles and sections from user input
Removed sections: None (new constitution)
Templates requiring updates:
  - .specify/templates/plan-template.md ⚠ pending
  - .specify/templates/spec-template.md ⚠ pending
  - .specify/templates/tasks-template.md ⚠ pending
  - .specify/templates/commands/*.md ⚠ pending
  - README.md ⚠ pending
Follow-up TODOs: None
-->

# Unified AI-Authored Technical Book with Embedded RAG Chatbot Constitution

## Core Principles

### I. Spec-First Development
All content and features must be driven by clear specifications. Every aspect of the book and chatbot functionality must be defined in specifications before implementation begins.

### II. Accuracy and Faithfulness
All book content must be accurate and faithful to the written material. No hallucinated concepts outside the defined book scope are allowed. Explanations must be concise, technically accurate, and internally consistent.

### III. Clarity for Mixed Technical Audience
Content must be clear and accessible to a technical but mixed audience including developers, students, and self-learners. All explanations should be structured with clear learning objectives and consistent hierarchy.

### IV. Deterministic Structure
The book generation process must be repeatable and reproducible. All steps must be automatable via Claude Code with deterministic structure ensuring consistent output across builds.

### V. Separation of Concerns
Maintain clear separation between content, infrastructure, chatbot, and data layers. Each component should be independently manageable and testable with well-defined interfaces.

### VI. Security and Correctness by Default
Security and correctness must be built in from the start. No hard-coded secrets or credentials allowed. All systems must follow security best practices by default.

## Content Standards
All book content must be written in Markdown (.md) and structured according to Docusaurus docs conventions. Each module and chapter must have clear learning objectives, consistent headings and hierarchy, and examples where applicable. No hallucinated concepts outside the defined book scope are permitted.

## Book Architecture
Framework: Docusaurus with deployment target of GitHub Pages. Sidebar configuration must reflect the logical structure of the book. All content files must be registered and navigable with no broken links or orphaned pages.

## RAG Chatbot Standards
The chatbot must answer questions using ONLY the indexed book content and user-selected text when provided. No external or world-knowledge answers unless explicitly included in the book. The chatbot must have clear refusal behavior when an answer is not present in the source material.

## Chatbot Architecture
Backend: FastAPI with embeddings & agent orchestration via OpenAI Agents / ChatKit SDKs. Vector database: Qdrant Cloud (Free Tier). Relational storage: Neon Serverless Postgres. Chunking, indexing, and retrieval must be deterministic and documented. Source attribution must be preserved internally for traceability.

## Constraints
No content outside the defined book scope. No undocumented assumptions. No hard-coded secrets or credentials. Free-tier compatible infrastructure only. All steps must be automatable via Claude Code.

## Quality Standards
Zero broken builds. Zero runtime errors in chatbot flows. Consistent terminology across book and chatbot. Clean, readable, and maintainable specifications.

## Success Criteria
Book builds successfully with Docusaurus. Book is deployed and accessible via GitHub Pages. RAG chatbot correctly answers questions about full book content and user-selected text only. Chatbot refuses unsupported queries correctly. Entire system is reproducible from specs alone.

## Governance

Constitution supersedes all other practices. All development must comply with these principles. Amendments require proper documentation and approval process. All implementation work must verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07