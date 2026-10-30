# Handoff

Interrupting or resuming a session. The two are never the same step.

1. The user wants to pause, the context is nearly full, or no handoff exists yet: read `handoff` and write the handoff doc plus the opening block.
2. The user wants to resume and gave a handoff path: read only that doc and restore the state from its opening block. Do not write a second handoff.

Done when: on a pause, the reply carries the absolute path and the opening block. On a resume, the reply carries the path you read and whether the doc's first re-verification command has been run.
