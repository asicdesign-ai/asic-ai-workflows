
# asic-ai-workflows

Open, structured repository of reusable AI workflows for ASIC and semiconductor engineering.

---

## Overview

This project aims to build a **practical, engineering-grade system of AI workflows** for chip design and verification.

The repository is organized around three core building blocks:

- **Skills** — reusable AI tasks for specific engineering problems  
- **Rules** — domain knowledge and constraints  
- **Flows** — multi-step workflows combining skills and rules  

The goal is to move from ad-hoc prompts to **structured, reusable, and testable AI artifacts**.

---

## Scope

This repository targets real-world semiconductor workflows, including:

- ASIC Design  
- Design Verification (DV)  
- Formal Verification  
- SoC Integration  
- Static Timing Analysis (STA)  
- Lint  
- Synthesis  
- Physical Design  

---

## Repository Structure

## Repository Structure

- `skills/` — Reusable AI engineering skills  
- `rules/` — Static domain knowledge and constraints  
- `flows/` — Multi-step engineering workflows  
- `schemas/` — Standardized definitions for all artifacts  
- `datasets/` — Example inputs for testing and validation  

Each component has a clear responsibility and is designed to be composable.
Each component has a clear responsibility and is designed to be composable.

---

## Core Philosophy

- GitHub is the **source of truth**
- The website is a **presentation layer**
- Focus on **content and functionality first**
- Prefer **structured artifacts over prompts**
- Build **reusable engineering workflows**

---

## What is a Skill?

A **skill** is a reusable AI capability that solves a specific engineering task.

Examples:

- STA Summary Analyzer  
- CDC Violation Classifier  
- Lint Warning Explainer  
- Simulation Failure Analyzer  
- UVM Test Generator  

Each skill is:

- Structured  
- Deterministic (as much as possible)  
- Backed by real examples  
- Designed for reuse across flows  

---

## What is a Rule?

A **rule** encodes domain knowledge or engineering best practices.

Example:

> Always analyze Worst Negative Slack (WNS) before Total Negative Slack (TNS)

Rules are used by:
- Skills
- Flows
- Agents

---

## What is a Flow?

A **flow** is a multi-step workflow that combines skills and rules.

Example: Timing Closure Flow

1. Run STA  
2. Extract worst paths  
3. Classify violations  
4. Suggest fixes  
5. Re-run timing  

---

## Development Strategy

The project follows a strict build order:

1. Create real, working skills  
2. Validate with datasets  
3. Add supporting rules  
4. Compose flows  
5. Build website later  

UI and presentation are intentionally delayed.

---

## Getting Started

This repository is in **early stage (foundation phase)**.

Recommended first steps:

1. Explore the `skills/` directory  
2. Review examples and outputs  
3. Use datasets to test behavior  
4. Contribute improvements or new skills  

---

## First Target Skill

The initial focus is:

> **STA Summary Analyzer**

Why:

- High value across all projects  
- Easy to validate  
- Strong demonstration of capability  

---

## Long-Term Vision

Build the largest open repository of:

> **AI-powered semiconductor engineering workflows**

Target users:

- ASIC engineers  
- DV engineers  
- Physical design engineers  
- SoC architects  
- Formal engineers  

---

## Contributing

Contributions are welcome, but must follow:

- Defined schemas  
- Structured formats  
- Engineering-grade quality  
- Reproducible examples  

Avoid:
- Unstructured prompts  
- Vague outputs  

---

## License

MIT License

---

## Future

Planned extensions:

- Skill chaining  
- Automated flow execution  
- Dataset benchmarking  
- Prompt optimization  
- Model comparison  

---

## Website (Planned)

A companion website will be launched later:

https://asicdesign.ai

The website will act as a **presentation and discovery layer**, not the core system.

---
