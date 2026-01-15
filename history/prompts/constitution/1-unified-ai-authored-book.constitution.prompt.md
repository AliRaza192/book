---
id: 1
title: Unified AI Authored Book Constitution
stage: constitution
date: 2026-01-07
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: aliraza
command: /sp.constitution
labels: [constitution, book, rag, chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
---

## Prompt

Project: Unified AI-Authored Technical Book with Embedded RAG Chatbot

Purpose:
Create a production-grade, AI/spec-driven technical book authored using Claude Code
and Spec-Kit Plus, published via Docusaurus and deployed to GitHub Pages, with an
embedded Retrieval-Augmented Generation (RAG) chatbot capable of answering
questions about the book's content, including user-selected text.

Core principles:
- Spec-first development (all content and features driven by clear specifications)
- Accuracy and faithfulness to written book content
- Clarity for a technical but mixed audience (developers, students, and self-learners)
- Deterministic structure (repeatable, reproducible book generation)
- Separation of concerns (content, infrastructure, chatbot, and data layers)
- Security and correctness by default

Content standards:
- All book content must be written in Markdown (.md)
- Content must be structured according to Docusaurus docs conventions
- Each module and chapter must have:
  - Clear learning objectives
  - Consistent headings and hierarchy
  - Examples where applicable
- No hallucinated concepts outside the defined book scope
- Explanations must be concise, technically accurate, and internally consistent

Book architecture:
- Framework: Docusaurus
- Deployment target: GitHub Pages
- Sidebar configuration must reflect the logical structure of the book
- All content files must be registered and navigable
- No broken links or orphaned pages

RAG chatbot standards:
- Chatbot must answer questions using ONLY:
  - The indexed book content
  - User-selected text (when provided)
- No external or world-knowledge answers unless explicitly included in the book
- Clear refusal behavior when an answer is not present in the source material

Chatbot architecture:
- Backend: FastAPI
- Embeddings & agent orchestration: OpenAI Agents / ChatKit SDKs
- Vector database: Qdrant Cloud (Free Tier)
- Relational storage: Neon Serverless Postgres
- Chunking, indexing, and retrieval must be deterministic and documented
- Source attribution must be preserved internally for traceability

Constraints:
- No content outside the defined book scope
- No undocumented assumptions
- No hard-coded secrets or credentials
- Free-tier compatible infrastructure only
- All steps must be automatable via Claude Code

Quality standards:
- Zero broken builds
- Zero runtime errors in chatbot flows
- Consistent terminology across book and chatbot
- Clean, readable, and maintainable specifications

Success criteria:
- Book builds successfully with Docusaurus
- Book is deployed and accessible via GitHub Pages
- RAG chatbot correctly answers questions about:
  - Full book content
  - User-selected text only
- Chatbot refuses unsupported queries correctly
- Entire system is reproducible from specs alone

## Response snapshot

The constitution file has been successfully created with the following principles and standards:

1. Spec-First Development - All content and features driven by clear specifications
2. Accuracy and Faithfulness - Content must be accurate with no hallucinated concepts
3. Clarity for Mixed Technical Audience - Accessible to developers, students, and self-learners
4. Deterministic Structure - Repeatable and reproducible book generation
5. Separation of Concerns - Clear separation between content, infrastructure, chatbot, and data layers
6. Security and Correctness by Default - Built-in security and correctness

The constitution includes detailed sections for Content Standards, Book Architecture, RAG Chatbot Standards, Chatbot Architecture, Constraints, Quality Standards, Success Criteria, and Governance. The version is set to 1.0.0 with ratification date of 2026-01-07.

## Outcome

- ✅ Impact: New constitution file created with all project principles defined
- 🧪 Tests: No tests required for constitution creation
- 📁 Files: 1 file created (.specify/memory/constitution.md)
- 🔁 Next prompts: Ready for spec creation based on these principles
- 🧠 Reflection: Constitution provides clear guidance for all project development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create feature specifications based on these principles