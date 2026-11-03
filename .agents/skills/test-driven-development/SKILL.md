---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code
model: sonnet
---

# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.
If you didn't watch the test fail, you don't know it tests the right thing.

## Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Delete it and start over. Don't keep it as "reference", don't adapt it.

Applies to: new features, bug fixes, refactoring, behavior changes.
Exceptions (ask your human partner): throwaway prototypes, generated code, configuration files.

## Cycle: Red → Green → Refactor

1. **RED** – Write one minimal test: one behavior, clear name, real code (mock only if unavoidable).
2. **Verify RED (mandatory)** – Run it. It must *fail* (not error), with the expected message, because the feature is missing. If it passes, you are testing existing behavior: fix the test.
3. **GREEN** – Write the simplest code that passes. No extra features, no refactoring of other code.
4. **Verify GREEN (mandatory)** – The test passes and output is clean. If it fails, fix the code, not the test.
5. **Run the project's whole suite** (bare `pytest`, `npm test`, `cargo test`, whatever the repo uses), even if the task named one file. A scope statement bounds the deliverable, not verification. Report every failure by name, including ones you didn't cause.
6. **REFACTOR** (only when green) – remove duplication, improve names, keep tests green, add no behavior. Then repeat.

When writing or changing any test, read [writing-good-tests.md](writing-good-tests.md).

## Example: bug fix

Bug: empty email accepted.
- RED: `test('rejects empty email', ...)` expects `error === 'Email required'`.
- Verify RED: `FAIL: expected 'Email required', got undefined`.
- GREEN: `if (!data.email?.trim()) return { error: 'Email required' };`
- Verify GREEN: suite passes.

## Common rationalizations (all mean: stop, delete the code, start with a test)

- "Too simple to test" / "Manual test is faster" / "Already tested it by hand": manual checks leave no re-runnable record.
- "I'll test after" / "Tests after serve the same purpose": a test written after the code passes immediately, so it proves nothing.
- "Keep it as reference" / "Deleting hours of work is wasteful": that is adapting, i.e. testing after. The time is already spent.
- "Need to explore first": fine, throw the exploration away, then start with a test.
- "Hard to test": the design is unclear. Simplify the interface, use dependency injection.
- "TDD is dogmatic" / "this case is different": rationalizing.

## When stuck

- Don't know how to test: write the wished-for API and the assertion first, or ask your human partner.
- Test setup is huge: extract helpers; still complex means simplify the design.

## Done checklist

- [ ] Every new function/method has a test, and I watched each fail for the expected reason first
- [ ] Minimal code written for each; the whole suite passes with clean output
- [ ] Edge cases and errors covered; mocks only where unavoidable

Production code exists only if a test existed and failed first. Otherwise it is not TDD. No exceptions without your human partner's permission.
