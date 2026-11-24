---
id: oak-gov-no-medical-advice
name: No medical advice
description: Blocks requests for a diagnosis, for changing a medication or dose, and about acute symptoms such as chest pain. General health information questions are still answered.
type: intent_guard
priority: 95
enabled: true
triggers:
  natural_language:
    - I have chest pain, what should I do
    - should I double my medication
    - should I stop taking my medication
    - what dose of medication should I take
    - do I have a heart attack
  threshold: 0.7
  target: intent
response_type: natural_language
allow_override: false
---
I can't give medical advice, a diagnosis, or tell you to change a medication. If this is an emergency, call 911 now. For other health questions, call the Oak 24/7 nurse line at 1-800-555-0199 or talk to your doctor. I can help you find an in-network provider or check what your plan covers.
