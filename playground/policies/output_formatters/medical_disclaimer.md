---
id: oak-gov-medical-info-disclaimer
name: Medical information disclaimer
description: Adds a not-medical-advice note to health condition answers.
type: output_formatter
priority: 80
enabled: true
triggers:
  keywords: [blood pressure, hypertension, diabetes, symptom, medical condition, treatment]
  target: agent_response
format_type: markdown
---
Keep the answer exactly as written. Append this note as the last paragraph, on its own line, in italics: *Not medical advice: this is general health information. Talk to your doctor or the Oak 24/7 nurse line (1-800-555-0199) about your own situation.*
