# Review of up-2022 (upstream PR #2022) by claude (claude-opus-5-5, review-v1)

**Verdict:** All four clauses met. A minor side effect is untested.

The change adds `if (type.IsAbstract) return false;` at the top of `FormatterDescriptor.TryCreate` (AnalyzerOptions.cs:221). Abstract formatters never become descriptors, so they can't produce MsgPack013 (no instance) or take part in MsgPack009 collisions. That fixes the cause, not a symptom. The new test `AbstractFormatterDoesNotAttractAttention` declares two abstract `IMessagePackFormatter<object>` types and expects no diagnostics. It fails on base source with MsgPack009 (tests.fail_without_fix) and passes on head. The full suite passes 150/150.

## Findings
- **C1 (minor, correctness):** `TryCreate` is also how a type named in `[MessagePackFormatter(typeof(X))]` (TypeCollector.cs:720) or `[MessagePackKnownFormatter(typeof(X))]` (AnalyzerUtilities.cs:95) gets resolved. If X is abstract, it is now silently treated as "not a formatter". The diagnostic in that branch is commented out (TypeCollector.cs:725), so the user gets no warning. On base the KnownFormatter path gave MsgPack013. No test covers this, and I did not run it.
- **C2 (info, tests):** the test covers only the analyzer. The generator's discovery uses the same `TryCreate`, so it is covered by construction but not by a snapshot test.

## Read beyond the context
The other `TryCreate` callers at head: TypeCollector.cs, Utils/AnalyzerUtilities.cs, GeneratorUtilities.cs and MsgPack00xMessagePackAnalyzer.cs.
