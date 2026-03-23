
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

- `skills/` — Reusable AI engineering skills  
- `rules/` — Static domain knowledge and constraints  
- `flows/` — Multi-step engineering workflows  
- `schemas/` — Standardized definitions for all artifacts  
- `datasets/` — Example inputs for testing and validation  

Each component has a clear responsibility and is designed to be composable.
Each component has a clear responsibility and is designed to be composable.

---

## Design Principles

This project follows a set of practical design principles:

- Focus on real engineering problems  
- Prefer structured, reusable artifacts over ad-hoc prompts  
- Ensure outputs are testable and reproducible  
- Build composable workflows from simple components  
- Prioritize functionality over presentation  

These principles guide the development of skills, rules, and flows.

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
