---
id: oak-gov-plan-advice-disclaimer
name: Plan advice disclaimer
description: Marks plan comparisons and switch answers as estimates.
type: output_formatter
priority: 80
enabled: true
triggers:
  keywords: [HDHP, PPO, HMO, switch plans, switching, compare plans, which plan, annual cost]
  target: agent_response
format_type: markdown
---
Keep the answer exactly as written. Append this note as the last paragraph, on its own line, in italics: *Estimate only, not a recommendation: costs depend on how much care you use. Check the plan documents or call Member Services before you change plans.*
