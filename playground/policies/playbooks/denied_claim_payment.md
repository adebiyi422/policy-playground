---
id: oak-gov-denied-claim-payment
name: Never pay a denied claim in collections
description: Do not pay a denied claim in collections. Explain the appeal option first.
type: playbook
priority: 90
enabled: true
triggers:
  natural_language:
    - pay everything I owe
    - pay all my bills
    - pay what I owe
    - pay the due payment
    - pay my bill
    - pay for claim
    - make a payment
  threshold: 0.7
  target: intent
---
# Never pay a denied claim in collections

## Rule
A claim that was denied and whose bill has status IN_COLLECTIONS must not be paid. The member can appeal the denial. Other bills that are due can be paid.

## Steps
1. Retrieve the billing items for the member. For each bill the member wants to pay, note its status.
2. Pay only bills with status DUE. Never create or confirm a payment intent for a bill with status IN_COLLECTIONS.
3. For a bill in collections, tell the member the claim was denied, that the bill is in collections, the amount, and the common reasons for a denial (a duplicate claim, or a service the plan does not cover). Tell the member they can appeal and ask whether they want help with that.
4. In the final answer, list which claims were paid and which were not paid, with the reason.
