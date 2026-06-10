---
name: thermal-overload-mitigation
description: Senior power-engineer playbook for overloaded lines and transformers. Use whenever power-flow or contingency studies show loading above ratings — including escalations from a tool skill where branch loading exceeds 100% of its rating. Triggers on "line overloaded", "transformer above rating", "relieve congestion", or "redispatch to unload". Gives an operationally credible sequence of redispatch, topology, phase-shifter, and reinforcement actions rather than only flagging the overload.
---

# Thermal overload mitigation

Start with the monitored element, the applicable rating, and the driving condition.

## Preferred action order
1. Confirm the overload is real: correct rating set, correct outage state, and solved base case or contingency.
2. Redispatch generation or transfer patterns to unload the corridor.
3. Reconfigure topology or switching where operations permit.
4. Use phase shifters, HVDC schedules, or transformer controls only when sensitivity evidence supports them.
5. If the issue is persistent, move to reconductoring, uprating, or new facilities.

## Working rules
- Separate normal-rating issues from emergency-rating issues.
- Fix the smallest set of elements that relieve the monitored overload cluster.
- Validate a candidate fix on all critical monitored contingencies, not just the worst case.
- Use PTDF or LODF style sensitivities when the software provides them.

## Deliver
- The overloaded elements and rating basis.
- The dispatch or topology changes that help most.
- The recommended corrective action and the residual risk.
