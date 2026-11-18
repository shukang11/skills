# Session stores

Recall reads this before it searches. A home directory that is missing is "not installed". A store that exists but holds no session text is "present, not a transcript". Do not invent a conversation for either.

Match the workspace first, then the window, then the topic. Order candidates by file modification time, never by the id in the name.

Skip the session that contains the current conversation. When you cannot tell which file that is, skip the newest matching file in this workspace and say which one.

## pi

`~/.pi/agent/sessions/<slug>/*.jsonl`

`<slug>` is `--` plus the workspace path with the leading slash removed and each `/` turned into `-`, plus `--`. `/Volumes/Storage/Documents/project/skills` is `--Volumes-Storage-Documents-project-skills--`.

The first line is `type: session` and carries `id`, `timestamp`, and `cwd`. The directory is already the workspace, so a matching directory does not need a second cwd check. User and assistant text are lines with `type: message`, then `message.role`.

## Cursor

`~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`

`<slug>` is the workspace path with the leading slash removed and each `/` turned into `-`. The file has no cwd. The directory is the workspace.

Lines are `role` plus `message.content`. Chats under `<uuid>/subagents/` are subagent runs. Skip them unless the parent session says the work happened there.

## Claude Code

`~/.claude/projects/<slug>/`

`<slug>` is the absolute path with each `/` turned into `-`, so the name starts with `-`. `/Volumes/Storage/Documents/project/Invest-Lab` is `-Volumes-Storage-Documents-project-Invest-Lab`.

Start at `sessions-index.json`. It has `originalPath` and `entries[]` with `sessionId`, `fullPath`, `projectPath`, `created`, `modified`, `gitBranch`, `summary`, `firstPrompt`, `messageCount`, and `isSidechain`. Use it to choose files. Skip `isSidechain: true`. The transcript is `<sessionId>.jsonl` in that directory. Its lines carry `type` (`user` or `assistant`), `cwd`, `sessionId`, and `timestamp`.

`~/.claude/transcripts/ses_*.jsonl` is not this store. Those files have no workspace. Leave them unread.

## Codex

`~/.codex/sessions/YYYY/MM/rollout-*.jsonl`

Files are not grouped by workspace. Read the first line only to decide. It is `type: session_meta`, and `payload.cwd` is the workspace. Open the rest of the file only after the cwd and the window match.

`~/.codex/archived_sessions` uses the same line when it contains `rollout-*.jsonl`. Treat those files as the same store.

## OpenClaw

`~/.openclaw-autoclaw/agents/<name>/sessions/*.jsonl`, and the same layout under `~/.openclaw/agents/` when that directory exists.

Skip `*.trajectory.jsonl` and `*.trajectory-path.json`. The first line is the same header pi uses: `type: session` with `cwd`. Keep a file only when that cwd is in scope.

`sessions.json` beside the files maps a chat id to `sessionFile`. The transcript is the `.jsonl` it names, not the index.

## Not a transcript

- `~/.gemini/history/<name>/.project_root` is one path and nothing else. When the path matches, report that the project was opened there. There is no chat to read.
- `~/.gemini/antigravity-cli/conversations/*.db` is sqlite. Report it as present and unreadable. Do not dump blobs.

## A store this file does not name

Look under that agent's home for a directory of session or transcript files. Read one header. Keep a file only when the header carries a workspace path in scope, or the file already lives in a directory that is that workspace. Write down the path rule you used. A store you cannot key to a workspace stays out.
