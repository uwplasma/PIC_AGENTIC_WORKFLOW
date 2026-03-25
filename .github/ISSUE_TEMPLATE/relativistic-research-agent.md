---
name: Relativistic Research Agent
about: PR-first agent task for momentum-space relativistic PIC research and implementation planning
title: "Relativistic milestone: "
labels: []
assignees: []
---

## Goal

Move PIC_AGENTIC_WORKFLOW one bounded step closer to a formally relativistic, momentum-space 1D3V PIC workflow that can later be upstreamed into JAX-in-Cell.

## Scope

- Work only in this repository.
- Do not modify JAX-in-Cell directly from here.
- Keep changes PR-first and narrowly scoped.
- Do not weaken any repository security or workflow restrictions.

## Required Prompt

Use the instructions in [agent/prompts/relativistic_research.md](/Users/rogerio/local/PIC_agentic_workflow/agent/prompts/relativistic_research.md).

## Milestone For This Issue

Describe one milestone only. Examples:

- define benchmark cases from literature for relativistic 1D3V electrostatic PIC
- add Maxwell-Juttner momentum-space sampling validation utilities
- add momentum-space schema and documentation for relativistic initialization
- add energy-conservation diagnostics and reporting for relativistic test cases
- write the upstream migration plan for converting JAX-in-Cell from velocity to momentum state variables

## Acceptance Criteria

- Open a PR against `main`.
- Include a scientific rationale in the PR body.
- Include tests, validation artifacts, or a clearly bounded research summary.
- End the PR with the next recommended milestone.