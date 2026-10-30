# Repo audit

Can an agent start work in this repo? Read-only; stop at the recommendation table.

1. Read `agent-ready-repository`. Do not execute remediation, do not sequence the priorities.
2. When the user accepts the recommendations and wants to start, read `correct`: fix each mistake class at the highest level that works (architecture, then types, then lint, then tests, with docs last) and prove each new check fails on a real past mistake.

Done when: the recommendation table is in the reply, every row carries a decidable exit, and an audit that found nothing states its scope.
