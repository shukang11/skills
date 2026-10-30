# The seven questions for any benchmark

Read when you produce a performance number: a PR's before and after, a regression claim, a choice between options, a hillclimb harness.

`principle-explain-the-number` gives the three-line rule; this is its execution sheet.

## Before you run anything

- Write the conclusion you expect to ship as one sentence, for example "p50 export is 30% faster on the 60k-row dataset". All seven questions test that sentence.
- Read the measurement script. Note what it times, what it counts, what it ignores.
- Check how busy the machine is: `uptime` and the core count. If something else is running, find out what. If you cannot stop it, interleave the two sides so both see the same noise, and say so in the report.

## The questions

1. **Why not double?** Name what limits it. Profile in a run you do not report, because profilers slow the work down: `top` or `pidstat` for per-process CPU, `node --cpu-prof`, `py-spy`, `perf`, I/O wait, `strace -c` for syscall counts, then map the hot spot back to source. Watch the load generator too: if it saturates first, you measured the load generator. If a change did not move the number, the limiter explains why, so find it before concluding anything.
2. **Was it tuned?** Run both sides the way production runs them: release builds, production flags, batch and transaction settings, connection pools, caches as warm or cold as production sees them, the same versions and data. One side on defaults means you compared configurations, not implementations. If you cannot tune it, pick no winner from that run.
3. **Did it break a limit?** Do the arithmetic: bytes per second against disk and network bandwidth, operations per second times cost per operation against your cores, the time saved against the time that piece itself took. Removing a piece that takes 10% of the run can make the run at most about 11% faster. A number past the limit measured something else: a cache, a no-op, or a bug.
4. **Did it error?** Count failures and non-success responses, and check that outputs are correct, not merely present. Rejections are often fast; timeouts and retries are slow. If the script does not count errors, add the count.
5. **Does it reproduce?** Run each side at least 5 times, alternating A, B, A, B, so warmup, lazy initialization, caches, and drift favour neither side. Report the median and the range. A gap smaller than the run-to-run variation is no measurable difference. When the call is close, use a rank-sum test or the harness's own statistics.
6. **Does it matter end to end?** Next to any micro result, measure the path a user actually waits on, with realistic data sizes and concurrency. A helper that takes 1% of a request can make the request at most 1% faster.
7. **Did the work even happen?** Confirm the work ran inside the timed region: the request reached the server, the rows were written, the bytes were read, the result was used. Lazy code (generators nobody iterates, promises nobody awaits, results the JIT discards) and timeouts both produce numbers for work that never happened.

## Report

- Lead with the verdict: faster, slower, no measurable difference, or inconclusive.
- Give the number with its unit, run count, range, and limiter, for example "p50 41 ms to 33 ms, median of 7 runs per side, range 32 to 35 ms after, bound by JSON parsing on one core".
- Call it inconclusive when you claim a difference but cannot name the limiter, when one side ran untuned, or when you could not check questions 4 and 7. Name the gap.
- One primary number in the PR body. Put the runs, range, and limiter evidence in a linked artifact or notes file.
