# Refactor

External behaviour unchanged; structure only.

1. Read `how-it-works` for the subsystem being moved.
2. Read `codebase-design` and write the public contract for the moved shape first.
3. Pin the current behaviour with a seam test before moving anything. Skip when a test already pins it.
4. Read `principle-sequence-verifiable-units` and `principle-laziness-protocol`, then move.
5. Read `principle-prove-it-works`. The check after the move is the same check as before it.
6. Read `principle-minimize-reader-load`: the measure of success is that reader load went down. When the diff does not lower the layers a reader traces or the state they hold, the change did not earn its keep; revert it.

When behaviour has to change, switch to [bug-fix.md](bug-fix.md) or [feature.md](feature.md) and say so. Do not open `code-simplify` unless the user separately asks for cleanup.

Done when: the same check actually ran before and after the move, both output summaries are in the reply, and you can name the layer or the state the move removed.
