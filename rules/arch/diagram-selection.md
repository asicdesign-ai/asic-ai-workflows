# Diagram Selection

Use this rule whenever a skill emits architecture documentation with diagrams.

## Required behavior

1. Add a diagram only when it clarifies behavior that would otherwise stay
   ambiguous in prose.
2. Use **WaveDrom** for cycle or handshake timing relationships.
3. Use **Mermaid** for FSMs, mode transitions, or ordered control flow.
4. Use **BlockDiag** for block-level structure, datapath partitioning, or major
   interface connectivity.
5. Keep diagrams grounded in the provided requirements and visible architecture
   assumptions.

## Prohibited behavior

- Do not emit diagrams as decoration.
- Do not use a diagram type for semantics it does not represent well.
- Do not invent states, ports, or timing phases that are not supported by the
  provided inputs.
