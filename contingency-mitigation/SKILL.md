---
name: contingency-mitigation
description: Senior power-engineer playbook for contingency violations. Use when N-1 or N-2 studies reveal voltage or thermal problems and the agent needs to move from ranking contingencies to identifying preventive or corrective actions.
---

# Contingency mitigation

Start with a solved base case and a ranked list of critical contingencies.

## Preferred action order
1. Verify the contingency definitions, monitored elements, and limits.
2. Group critical contingencies by common corridor, interface, or weak area.
3. Apply preventive actions first: redispatch, shunts, tap changes, or topology changes that help multiple contingencies.
4. Evaluate corrective actions next: post-contingency switching, redispatch, or RAS schemes with explicit triggers.
5. Use load shedding only as a last-resort action and state that clearly.
6. For recurring problems, recommend reinforcement or a revised operating guide.

## Working rules
- Do not trust contingency results from a bad base case.
- Prefer actions that improve a family of contingencies rather than a single outage.
- Re-run the full monitored set after any candidate fix.

## Deliver
- The critical contingencies and the shared weak pattern.
- The best preventive action.
- Any corrective action that is still required after prevention.
