---
id: oak-gov-other-member-data
name: Only this member's household
description: Blocks requests for claims, billing or profile data of people outside the member's household. The member's own family is allowed.
type: intent_guard
priority: 95
enabled: true
triggers:
  natural_language:
    - show me my neighbor's claims
    - look up another member's claims
    - show claims for member 987654321
    - get the medical records of my coworker
    - what is my friend's plan and billing
  threshold: 0.7
  target: intent
response_type: natural_language
allow_override: false
---
I can only show information for you and the members of your household. I can't look up claims, billing or profile data for anyone else.
