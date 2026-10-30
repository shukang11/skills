# ASD-STE100 quick rules and replacement table

This file answers: which words and sentence shapes break the rule, and what to write instead.

## Length limits

| Text type | English limit | Shape allowed |
| --- | --- | --- |
| Procedural instruction | 20 words | imperative verb, one instruction |
| Descriptive statement | 25 words | active voice, one fact |

## Banned adjectives and vague words

| Offender | Problem | Rewrite direction |
| --- | --- | --- |
| properly, adequately | no boundary, cannot be judged | state the number or condition, such as "the gap is under 0.5%" |
| easily | a feeling | state the number of steps or the precondition |
| sufficiently | no threshold | state the threshold, such as "at least 3 retries" |
| normal, reasonable | relies on unstated agreement | list the accepted inputs or the state-machine condition |
| various, numerous | carries no information | list the items, or say how many |
| fast, rapid | unquantified | state milliseconds, throughput, or complexity class |

## Rewriting instructions

| Wrong (passive or hedged) | Right (imperative or active) |
| --- | --- |
| The user should ensure the config file is properly updated | Update the config file |
| The database will be initialized | The init script creates the database |
| It is recommended to run the tests before changing code | Run the tests before changing code |
| The system is able to handle exceptions automatically | The handler catches the exception and writes `error.log` |

## Word swaps

| Fancy | Plain |
| --- | --- |
| utilize, leverage | use |
| facilitate | help |
| numerous | many |
| in the event that | if |
| in order to | to |
| due to the fact that | because |
| serves as, boasts, features | is, has |
| delve into | read, investigate |
| enhance | improve, add |

## Sentence shapes to cut

- "Not just X, but Y": state Y.
- Forced groups of three: use the real number.
- Same idea in three synonyms: pick one and repeat it.
- "from X to Y" where the two ends are not on one scale: list the items.
- A colon mid-sentence as a connector: end the sentence instead.
- An em dash: end the sentence, or use a comma.
- An adverb propping up a weak verb: use the stronger verb or the number.
