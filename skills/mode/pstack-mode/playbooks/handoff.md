# Handoff

Interrupting or resuming a session. Pause and resume are never the same step.

1. The user wants to pause, or the context is nearly full: read `handoff` and write the handoff doc plus the opening block.
2. The user wants to resume and gave a handoff path: read only that doc and restore the state from its opening block. Do not write a second handoff.
3. The user wants to resume and gave no handoff path: read `recall`. Do not write a handoff to fill the gap.

Done when: on a pause, the reply carries the absolute path and the opening block. On a resume from a handoff, the reply carries the path you read and whether the doc's first re-verification command has been run. On a resume with no handoff, the reply is `recall`'s brief.
