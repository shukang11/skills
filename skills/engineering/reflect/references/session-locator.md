# Session locator

Read in step 1 when no transcript path was handed to you. One job: find *this* conversation's transcript on the harness you are running in, or report that no complete one is reachable.

Mining earlier sessions of the same project is `recall`; reflect reads only the run it is reviewing.

## Rules

- **Order**: an id or path the author or harness supplied, then the harness's own store, then a partial digest.
- **One project.** Another project's sessions stay unread, even when the topic matches.
- **Metadata decides.** The session id, the project path, and the first user request, together. A recent file holding none of this conversation's turns is a different session.
- **One file at a time.** Read a header line or an index row, then open the one file it points at. Never grep a whole store for a phrase to find the session.
- **Live versus archived.** An `archived` area or an `archived` flag marks closed runs. A closed run of an earlier conversation is history, never this session; when it is the only match, fall back to the digest and say so.
- **Compressed files** (`*.zst`, `*.zstd`) are read only with a decoder already on the machine (`zstd -dc <file>`). Without one, name the missing decoder and fall back to the digest; installing one is out of scope.
- **Any read mechanism counts**: `head -1` in a shell, a short script, or the harness's own file read. What matters is the line you matched, not which tool read it.

## pi

`~/.pi/agent/sessions/--<cwd-slug>--/*.jsonl`, where `<cwd-slug>` is the absolute cwd with the leading `/` dropped, each `/` turned into `-`, and the whole wrapped in `--`.

Header line: `type` is `session`, with `id`, `timestamp`, and `cwd`. Match the id the harness gave you, or the cwd. Then the first line whose `type` is `message` and whose `message.role` is `user` is the first user request. Order candidates by mtime, check each header, and open only the one that agrees.

## Codex

`~/.codex/sessions/<YYYY>/<MM>/<DD>/rollout-*.jsonl`, sometimes stored as `rollout-*.jsonl.zst`. `~/.codex/archived_sessions/` uses the same file shape when it holds files.

The store is not grouped by project. Line 1 is `type: session_meta` with `payload.cwd`, `payload.id` (also `session_id`), and `payload.timestamp`. Match that line: cwd, the id the harness gave you, the time window. The first entries with `payload.role` of `user` then settle the first request. Read the rest of the file only after the three agree. An archived rollout is history unless its id, cwd, and first request are this run's.

## Cursor

Prefer the path the harness exposes for this chat. Otherwise `~/.cursor/archive/index.jsonl` carries one JSON row per conversation: `conversation_id`, `workspace`, `title`, `created_at`, `updated_at`, `archived`, and `transcript`, a path relative to `~/.cursor/archive/`.

Filter rows by `workspace` equal to this project's path, or to a former path of the same repo confirmed by matching files rather than by a similar name. Then by time window, then by the first user request. Open only the row's `transcript`. `_unknown-workspace` and other placeholder names are not aliases. Transcript lines carry `role`, `message.content`, and `ts`; the first `role` of `user` is the request.

## DSH

`~/.dsh/sessions/--<cwd-slug>--/session-*/session.v4.jsonl.zstd`, same slug rule as pi. Compressed: `zstd -dc <file> | head -1` with the decoder present.

The header carries `type`, `id`, `createdAt`, and `cwd`. Match `cwd`, then the `id` and `createdAt` the harness exposed, and read the file when they agree.

## A harness not on this list

Take the session path or id the harness hands you. Failing that, the session-store inventory in `recall` names Claude Code, OpenClaw, and the directories that look like transcripts but are not. Its header rule carries over: keep a file only when its header holds this project's path, or the file already sits in a directory named for this project.
