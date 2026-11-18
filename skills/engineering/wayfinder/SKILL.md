---
name: wayfinder
description: "Plan work whose destination is clear but whose route is not: chart a map of decision tickets under handoff/wayfinder/ and resolve one ticket per session until the way is clear. Plans; never writes the implementation."
disable-model-invocation: true
argument-hint: "the destination; or the existing handoff/wayfinder/<slug>/map.md"
---

# Wayfinder

For work whose destination can be named but whose route cannot. Split it into decision tickets one session can resolve. The map is an index; the decisions live on the tickets. This skill plans and does not write implementation.

## Where it lives

One effort, one directory; the slug is the destination in kebab case:

- Map: `handoff/wayfinder/<slug>/map.md`
- Tickets: `handoff/wayfinder/<slug>/issues/NN-<slug>.md`, numbered from `01`, one file per ticket

Build only this directory. Do not touch `handoff/active.md`, do not create `handoff/ctx/`, do not write `.scratch/`.

`handoff/` is a temporary layer: clear it and the map and tickets go with it. Anything that has to outlive that goes to `.agents/notes/`, and the ticket's Answer becomes a pointer to that note plus a one-line gist. Terminology goes to `ALIGNMENT.md`; contracts go to the `docs/` topic that owns them. The map and tickets never restate that prose.

## Criteria

- Write the destination into the map before writing any ticket. The destination is the end of the whole map, not the end of this session.
- A ticket's body is a question that can be asked precisely right now. What cannot be asked yet stays in the map's "Not yet specified"; do not open a ticket for it.
- One ticket does one thing: `grilling`, `prototype`, `research`, or `task`.
- The frontier is every ticket with `Status: open` whose `Blocked by` tickets are all `resolved`. Take the lowest number first.
- Claim before any work: write `Status: claimed` and save, then start asking, looking, or simulating.
- One ticket per session. The charting session only creates files; it answers nothing.
- `grilling` and `prototype` answers are the human's call. The agent may recommend; it never writes the Answer for them.
- A `task` ticket exists only to unblock a decision: credentials, an account, moving data somewhere you can see it.
- The map's Notes never turn this session into implementation.
- Refer to tickets by title in the reply. Use relative paths between files.

## The four ticket types

| Type | When | How it resolves |
|---|---|---|
| `grilling` | The decision is one a conversation can settle. The default | Read the `grilling` skill and `domain-modeling`. Write the Answer only after the human confirms |
| `prototype` | The decision needs the logic or interaction seen before it can be made | Read `prototype`. The Answer points at `prototypes/index.html` and the behaviour the human picked |
| `research` | The decision is stuck on a fact outside the repo | The agent looks it up; the Answer carries the finding and the path or link it came from |
| `task` | Nothing to decide, but one thing blocks the decision | Do the unblocking work; the Answer says what was done |

`Blocked by:` takes ticket numbers, comma separated, such as `01, 03`. Empty when nothing blocks it.

## Map skeleton

```markdown
# <short name for the destination>

## Destination
<what is in hand when the whole map is done>

## Notes
<only constraints for this effort. Never "we can start implementing">

## Decisions so far
- <one-line gist> — issues/NN-<slug>.md

## Not yet specified
- <things you can feel coming but cannot ask precisely yet>

## Out of scope
- <what lies beyond the destination>
```

## Ticket skeleton

```markdown
# <the question>
Type: grilling
Status: open
Blocked by:

## Question
<one question>

## Answer
```

## Steps

No `map.md` yet:

1. Ask for the destination. No tickets before the human names it.
2. When the whole route is one question that can be asked now and settled in one session, stop and go to `grilling` instead.
3. Otherwise write the map and the tickets that can be asked now. Keep the fog in "Not yet specified". Anything beyond the destination goes to Out of scope, not to an open ticket.
4. Reply with the frontier tickets' titles and paths. This session writes no Answer.

Map exists:

1. Read only `map.md` and the first three lines of each ticket. Full body only for the ticket you are taking.
2. No frontier ticket: the map is clear. Reply with the `map.md` path; the next step is `to-spec`. This session writes no implementation.
3. Claim the lowest-numbered frontier ticket.
4. Resolve it by its Type. For a human-owned ticket, write the answer into `## Answer` and set `Status: resolved` only after the human confirms.
5. Add one line to Decisions so far. Fog that has become precise enough graduates into a new ticket and loses its line under "Not yet specified".
6. Reply with this ticket's title, the file its answer landed in, and the next frontier ticket's title. Then stop.

## Done when

- Charting session: `map.md` carries a destination the human gave; every ticket has a Type, `Status: open`, and a `## Question`; no ticket has an Answer body.
- Working session: exactly one ticket went `open` → `claimed` → `resolved`, and the map gained one line with a relative path.
- Every ticket in the reply is named by title and carries its `handoff/wayfinder/<slug>/` path.

## Output

`handoff/wayfinder/<slug>/map.md` plus `issues/NN-<slug>.md`.
