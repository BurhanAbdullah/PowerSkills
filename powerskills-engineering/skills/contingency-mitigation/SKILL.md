---
name: contingency-mitigation
description: Senior power-engineer playbook for contingency violations. Use whenever N-1 or N-2 studies reveal voltage or thermal problems, binding contingencies, or post-outage islanding — including escalations from a tool skill's contingency run. Triggers on "N-1 violation", "worst contingency", "preventive vs corrective action", or "do we need a RAS". Moves from ranking contingencies to identifying preventive and corrective actions that cover a family of outages.
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
