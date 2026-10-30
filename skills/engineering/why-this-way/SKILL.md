---
name: why-this-way
description: "Trace why a piece of code has the shape it does: design rationale, tradeoffs, regressions, postmortems, data-backed thresholds. Investigates every evidence source this environment actually has, in parallel, then returns a cited read. Use how-it-works for runtime behaviour."
disable-model-invocation: true
argument-hint: "the symbol, file, or named decision whose motivation you want"
---

# Why this way

Investigate the motivation and intent behind code. The `how-it-works` skill answers what the code does; this one answers what forces gave it that shape.

## Operating posture

Operate as a careful, cautious, precise investigator. Be honest about what you know versus what you are inferring. Every claim's wording comes from [references/epistemics.md](references/epistemics.md); read it before you write a line of output.

## 1. Understand the target and the question

The **target** is usually a chunk of code, a pattern, a feature, or a named decision. The **question** is usually a rationale, a tradeoff, a motivating edge case, an external constraint, dead code, or a broad history sweep.

If the target is vague ("why do we do it this way?" with no clear referent), take your best reading from the conversation, state it in one line so the user can redirect, then proceed. Do not stall on the ambiguity.

## 2. Build the code anchor

Before spawning anything, assemble the seed context yourself: file paths and line ranges, key symbols, the commits that last touched the target, PR numbers from merge subjects (`(#1234)`), and any linked ticket ids.

```bash
git blame -L <start>,<end> <file>        # last touch per line
git log --follow -p -- <file>            # full history through renames
git log --oneline -20 -- <file>          # recent commits with PR numbers
git log -1 --format=%B <commit>          # PR number out of the message
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,comments,reviews
```

That anchor goes to every investigator.

## 3. Investigate every source this environment has

**Default to full parallel coverage.** One investigator per evidence source, all spawned in one message, each owning exactly one source. The goal is a coverage map, not a minimal one: a source that came back empty is a finding, not a gap to hide.

Source control through `git` and `gh` is always available. Everything else depends on what is installed here:

1. **Source control** (git history, PR bodies, comments, tests). Best at implementation-time rationale captured during review.
2. **Issue or ticket tracker** (a Linear, Jira, GitHub Issues, Plane MCP). Best at the product or business forcing function.
3. **Long-form documents** (Notion, Confluence, Docs, Coda MCP). Best at design rationale written before code.
4. **Real-time team chat** (Slack, Discord, Teams MCP). Best at deliberation that never reached a doc.
5. **Infrastructure observability** (Datadog, New Relic, Honeycomb MCP). Best at the runtime reality that motivated the code.
6. **Error tracking** (Sentry, Rollbar MCP). Best at the exceptions that motivated defensive code.
7. **Analytics warehouse** (Databricks, Snowflake, BigQuery MCP). Best at the data reality behind flags, experiments, and thresholds.

Also read the repo's own record: `.agents/notes/` and `docs/`. When a project keeps its rationale there, that is usually the strongest source you have.

Skip a source only with a written reason that goes into the Sources section: **no such tool is installed here** (flag it as a gap, not a choice) or **the source is provably irrelevant** (a build-time script with no runtime path has no error-tracker story). "Probably irrelevant" is not a reason.

## 4. Weigh every finding

Each finding goes into exactly one confidence tier from [references/epistemics.md](references/epistemics.md): Direct, Supported, Inferred, Speculative, Unknown. The tier sets its section and its phrasing. When you edit the wording later, the tier does not move.

If the code looks defensive (null checks, retries, timeouts, rate limits, feature flags, OOM handling), spend extra effort on what event it was defending against.

## 5. Present

Write it yourself, in this order, cutting sections that carry nothing:

1. **The question**, as you understood it.
2. **The code in question**, with the anchor.
3. **What we found**: Direct and Supported claims, each cited.
4. **What we can reasonably infer**: Inferred claims, each with its chain spelled out.
5. **Competing hypotheses**: Speculative ones, side by side. Never promote one to an answer.
6. **What we don't know**: Unknown, with the specific searches that came back empty.
7. **Sources**: one line per source, including the ones that returned nothing and the ones that are not installed, each with its reason.
8. **Confidence summary**.

When the question is a precursor to changing this code, close with the constraint set the findings imply: what to preserve, what to change, what to avoid, where the risk is.

## Failure modes

- **Recency bias.** The most recent commit is not automatically the authority. Current shape is usually the accretion of several earlier decisions; trace back.
- **Confident wording on thin evidence.** The word "because" is reserved for Direct and Supported.
- **Hiding the null.** A source you searched and found nothing in is the most useful line in the reply when the user assumed it existed.

## Done when

- Every claim sits in one of the five tiers, and every Direct or Supported claim carries a commit, PR, path, or note location.
- The Sources section lists each source consulted, including empty ones and uninstalled ones with a reason.
- Competing explanations are listed, not silently resolved.
