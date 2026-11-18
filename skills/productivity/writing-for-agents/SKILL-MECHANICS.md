# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Codex reads invocation policy from `agents/openai.yaml`, beside `SKILL.md`:

```yaml
policy:
  allow_implicit_invocation: false
```

- **Automatic invocation**: set the value to `true`. Codex can include the skill in the model context for automatic selection. Keep the description precise and tied to a distinct task.
- **Explicit invocation**: set the value to `false`. Codex does not inject the skill into the model context by default. The human can still invoke it with `$skill-name` or the skill picker. This is the default choice for this repository. A missing policy defaults to automatic invocation in Codex, so every skill carries an explicit value.

`disable-model-invocation: true` in `SKILL.md` is retained for Claude Code. It does not replace Codex's policy. Claude Code's explicit-invocation semantics must not be assumed to describe Codex.

The source repository's `scripts/configure-codex-skills.py` owns the Codex allowlist. Run it to check every skill; use `--write` to apply the policy. New skills default to explicit invocation. The script preserves custom configuration by refusing to overwrite additional fields; merge those by hand.

Explicit invocation controls discovery. It does not prevent an already selected playbook from reading another skill's `SKILL.md` by a concrete file path. Keep shared references reachable by file links. This lets a manually selected router read its leaves without making every leaf automatically discoverable.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When explicit-only skills multiply past what you can remember, use a **router skill**: one explicitly invoked skill that names its leaves and gives their file paths. In Codex, the selected router reads those files as reference. This does not require enabling automatic discovery for the leaves.
