# Historical replay: real MessagePack-CSharp PRs routed by Countersign's deterministic stage

**Real data** (`simulated: false`): 109 merged upstream PRs, their real diffs, and escapes labelled by the rule in [README.md](README.md) (every label and its link: [labels.yaml](labels.yaml)). Mandate `mandate/messagepack.mandate.yaml` v5 as signed, sha256 `0b09c5be0fec`; no reviews, no models, no builds.

Reviewers can only add reasons to route to a human, never remove one, so these tiers are the most lenient Countersign could give: escapes in the cleared bucket are an upper bound on what the AI would have let through.

## Mode `ci-credited`

- Routed to a human (ask/block): **85 of 109** (78%); tiers: silent 0, notify 24, ask 74, block 11
- Escapes in the dataset: 11 (6 high-confidence)
- **Escapes Countersign would have cleared: 0 of 11**
- Upstream's real time from PR opened to merged (median days, human review as it happened): cleared bucket 0.24, routed bucket 0.85

| | routed to human | cleared by AI |
|---|---:|---:|
| escape (reverted / follow-up fix) | 11 | 0 |
| no escape found | 74 | 24 |

## Mode `diff-only`

- Routed to a human (ask/block): **109 of 109** (100%); tiers: silent 0, notify 0, ask 95, block 14
- Escapes in the dataset: 11 (6 high-confidence)
- **Escapes Countersign would have cleared: 0 of 11**
- Upstream's real time from PR opened to merged (median days, human review as it happened): cleared bucket None, routed bucket 0.75

| | routed to human | cleared by AI |
|---|---:|---:|
| escape (reverted / follow-up fix) | 11 | 0 |
| no escape found | 98 | 0 |

## Every PR

| PR | Merged | Title | Files | Lines | Escape | ci-credited tier | score | diff-only tier | Decisive drivers (ci-credited) |
|---|---|---|---:|---:|---|---|---:|---|---|
| [#1634](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1634) | 2023-08-13 | Union type collect | 2 | 24 | - | ask | 53.0 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#1667](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1667) | 2023-08-15 | Switch from MSBuild properties to an AdditionalFiles json file | 24 | 426 | - | ask | 57.0 | ask | trust cap: build-config; trust cap: unmapped; risk score: risk |
| [#1674](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1674) | 2023-09-11 | Fix analyzer when only MessagePack.Annotations is referenced | 3 | 11 | - | notify | 23.4 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1698](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1698) | 2023-11-07 | Support to analyze records | 4 | 144 | - | notify | 29.8 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1727](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1727) | 2024-01-10 | .NET 8 Update(1): stylecop related small update | 4 | 51 | - | ask | 56.0 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; mandate rule: dependency-check-failed; trust cap: build-config; trust cap: unmapped; r |
| [#1728](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1728) | 2024-01-10 | .NET 8 Update(2): TargetFrameworks | 33 | 1354 | - | ask | 120.0 | block | mandate rule: public-api-change; trust cap: build-config; trust cap: runtime-core; trust cap: unmapped; risk score: risk |
| [#1729](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1729) | 2024-01-11 | .NET 8 Update(3): Microsoft.CodeAnalysis.Analyzers v3.3.4 | 3 | 8 | - | ask | 53.3 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; trust cap: build-config; risk score: risk |
| [#1730](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1730) | 2024-01-12 | .NET 8 Update(4): System.Collections.Frozen | 4 | 304 | - | ask | 96.2 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1736](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1736) | 2024-01-22 | Source Generator configuration via attributes instead of .json file | 262 | 9936 | - | block | 105 | block | mandate rule: split-large-change |
| [#1743](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1743) | 2024-01-30 | AOT by default | 84 | 1857 | - | block | 97.9 | block | mandate rule: split-large-change |
| [#1754](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1754) | 2024-01-30 | Add a `[CompositeResolver]` attribute that triggers source generation | 22 | 750 | yes (medium) | ask | 89.6 | ask | mandate rule: public-api-change; trust cap: runtime-core; trust cap: unmapped; risk score: risk |
| [#1796](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1796) | 2024-04-11 | Include all hand-written formatters in the source generated resolver | 135 | 4051 | yes (medium) | block | 89.1 | block | mandate rule: split-large-change |
| [#1798](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1798) | 2024-04-13 | Fix source generated formatters for records with string keys | 6 | 347 | - | notify | 28.9 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1802](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1802) | 2024-05-07 | Source generated formatters that support private members | 212 | 3414 | yes (medium) | block | 90 | block | mandate rule: split-large-change |
| [#1818](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1818) | 2024-05-16 | Fix source generator handling of inaccessible custom formatters | 15 | 314 | - | ask | 45.0 | ask | risk score: risk |
| [#1824](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1824) | 2024-05-22 | Add `ExcludeFormatterFromSourceGeneratedResolverAttribute` | 6 | 75 | - | ask | 29.0 | ask | trust cap: unmapped |
| [#1842](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1842) | 2024-06-06 | Preserve code comments when adding attributes to fields | 2 | 41 | - | notify | 23.6 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1850](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1850) | 2024-06-21 | Fix handling of formatters following the singleton pattern | 18 | 384 | - | ask | 45.8 | ask | risk score: risk |
| [#1859](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1859) | 2024-06-28 | Report missing `[MessagePackObject]` attribute for generic types  | 3 | 92 | - | notify | 26.7 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1734](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1734) | 2024-07-01 | Unity consumes messagepack as a nuget package instead of source | 452 | 17214 | - | block | 120.0 | block | mandate rule: split-large-change |
| [#1874](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1874) | 2024-07-05 | Fix issues about the equality of AnalyzerOptions and FormatterDescript | 1 | 30 | - | ask | 52.2 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#1873](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1873) | 2024-07-17 | Fix some source generator issues | 12 | 257 | - | ask | 66.8 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#1872](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1872) | 2024-07-18 | Faster multi-element serialization for primitive types | 6 | 2659 | yes (high) | ask | 106.1 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1888](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1888) | 2024-07-19 | Remove Unity related symbols from Nuget projects | 17 | 254 | - | block | 137.1 | block | risk score: risk |
| [#1890](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1890) | 2024-07-19 | Simd Accelerated bool[] deserialize | 4 | 299 | - | ask | 74.0 | ask | trust cap: runtime-core; risk score: risk |
| [#1884](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1884) | 2024-07-19 | Avoid regenerating all formatters when only one object/union/enum chan | 6 | 100 | - | notify | 30.0 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1893](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1893) | 2024-07-22 | Offer code fix for MsgPack011: `partial` modifier required | 11 | 399 | yes (medium) | ask | 67.0 | ask | mandate rule: public-api-change; risk score: risk |
| [#1898](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1898) | 2024-07-22 | Offer code fix to ignore unattribute members of MessagePackObject type | 5 | 159 | - | ask | 51.4 | ask | mandate rule: public-api-change; risk score: risk |
| [#1905](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1905) | 2024-07-27 | Fix and improve generated formatters | 7 | 425 | - | notify | 32.3 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1907](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1907) | 2024-07-29 | Honor `ExcludeFormatterFromSourceGeneratedResolverAttribute` by suppre | 6 | 126 | - | notify | 28.6 | ask | trust cap: generator-analyzer-core; trust cap: build; risk score: risk |
| [#1910](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1910) | 2024-07-30 | Fix diagnostic and code fix for MsgPack011 on nesting types | 6 | 163 | - | notify | 32.5 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1912](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1912) | 2024-07-31 | Make source generation cancellable | 1 | 5 | - | ask | 51.2 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#1921](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1921) | 2024-08-06 | Fix some source generator issues | 6 | 34 | - | notify | 26.8 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1926](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1926) | 2024-08-18 | Lower language version requirement of source generated resolver | 74 | 876 | - | block | 77.9 | block | mandate rule: split-large-change |
| [#1936](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1936) | 2024-08-22 | Add ignore case option to EnumAsStringFormatter | 8 | 235 | - | ask | 97.4 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1960](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1960) | 2024-09-25 | Improve handling of array types in source generation | 21 | 957 | yes (medium) | ask | 60.5 | ask | risk score: risk |
| [#1962](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1962) | 2024-09-25 | Honor key name overrides in source-generated formatters | 3 | 113 | - | ask | 62.5 | ask | mandate rule: public-api-change; trust cap: annotations-api; risk score: risk |
| [#1946](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1946) | 2024-09-25 | Adjusted MsgPack004 to support records | 3 | 218 | - | notify | 31.7 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#1959](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1959) | 2024-09-25 | Add `MessagePackSerializer.Typeless.Deserialize` overload that takes ` | 6 | 7 | - | ask | 91.3 | ask | mandate rule: public-api-change; mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#1922](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1922) | 2024-09-25 | Support formatters for CompositeResolverAttribute | 14 | 139 | - | ask | 73.3 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1968](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1968) | 2024-09-26 | Make `CompositeResolverAttribute` much more useful | 34 | 693 | - | ask | 95.5 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1969](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1969) | 2024-09-27 | Add MsgPack014 analyzer and code fix | 6 | 262 | - | ask | 56.5 | ask | mandate rule: public-api-change; risk score: risk |
| [#1970](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1970) | 2024-09-27 | Avoid GetSemanticModel in analyzer | 2 | 88 | yes (high) | ask | 55.5 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#1978](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1978) | 2024-10-02 | Update DynamicAssembly usage to honor different AssemblyLoadContext's | 7 | 240 | - | ask | 96.6 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1971](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1971) | 2024-10-02 | Fix detecting duplicate keys | 2 | 187 | - | ask | 44.5 | ask | trust cap: runtime-core; risk score: risk |
| [#1980](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1980) | 2024-10-02 | Add AOT formatter support for init properties and required members | 13 | 288 | - | ask | 40.9 | ask | risk score: risk |
| [#1982](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1982) | 2024-10-03 | Fix analyzers to not mis-interpret source generated formatters as user | 1 | 6 | - | ask | 51.2 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#1981](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1981) | 2024-10-07 | Replace DynamicMethod use with private-capable Ref.Emit | 9 | 1210 | yes (high) | ask | 109.0 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1987](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1987) | 2024-10-07 | Reader/Writer touch-ups | 4 | 38 | - | ask | 85.5 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1990](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1990) | 2024-10-08 | Reconcile AllowPrivate behavior | 46 | 1236 | - | ask | 95.4 | ask | mandate rule: public-api-change; trust cap: runtime-core; trust cap: annotations-api; risk score: risk |
| [#2000](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2000) | 2024-10-15 | Fix embedded types being generated in resolver | 4 | 89 | - | ask | 54.5 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#2002](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2002) | 2024-10-15 | Migration improvements: deserializing constructors and less-frequent ` | 7 | 183 | - | notify | 29.6 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2003](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2003) | 2024-10-15 | Add analyzers to help recognize breaking changes | 9 | 439 | - | ask | 66.6 | ask | mandate rule: public-api-change; risk score: risk |
| [#2006](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2006) | 2024-10-16 | Fix handling of name collisions in type hierarchies | 20 | 465 | - | ask | 78.2 | ask | mandate rule: public-api-change; risk score: risk |
| [#2015](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2015) | 2024-10-17 | Use a collision-resistant hash algorithm for untrusted data | 6 | 650 | - | ask | 106.0 | ask | mandate rule: public-api-change; trust cap: runtime-core; trust cap: security-tests; risk score: risk |
| [#2013](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2013) | 2024-10-18 | Secure by default | 5 | 29 | yes (high) | ask | 61.2 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#2016](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2016) | 2024-10-18 | Avoid collecting members when it doesn't have [Key] | 4 | 178 | - | notify | 26.5 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2021](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2021) | 2024-10-18 | Add `scoped` modifier to `in` parameters of `ref struct` | 7 | 29 | - | ask | 88.2 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#2022](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2022) | 2024-10-18 | Ignore abstract implementations of `IMessagePackFormatter<T>` | 2 | 29 | - | notify | 23.2 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2023](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2023) | 2024-10-18 | Suppress MsgPack004 on private base members when only public is intere | 2 | 49 | - | notify | 24.0 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2028](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2028) | 2024-10-21 | Avoid collecting fields with custom formatter recusively | 9 | 568 | - | notify | 37.5 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2030](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2030) | 2024-10-22 | Support nesting formatters within generic data types | 34 | 1229 | yes (high) | ask | 57.0 | ask | mandate rule: generated-files; risk score: risk |
| [#2029](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2029) | 2024-10-22 | Apply scoped in more places | 6 | 30 | - | ask | 117.2 | ask | mandate rule: public-api-change; mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2031](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2031) | 2024-10-22 | Use generic type argument used for custom formatters | 4 | 155 | - | notify | 25.7 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2032](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2032) | 2024-10-22 | Use simpler C# syntax for nullable value types | 2 | 5 | - | ask | 52.1 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#2033](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2033) | 2024-10-23 | Fix simplified name for ValueTuple<T> | 4 | 185 | - | notify | 25.7 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2036](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2036) | 2024-10-23 | Avoid crashing with stack overflow on recursive generic type parameter | 8 | 172 | - | notify | 31.0 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2037](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2037) | 2024-10-25 | Fix mis-fire of `MsgPack003` on use of `Collection<T>` | 4 | 170 | - | notify | 26.1 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2026](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2026) | 2024-10-25 | Refactor reading fixint, fixmap, fixarray, fixstr | 6 | 357 | - | ask | 75.9 | ask | trust cap: runtime-core; risk score: risk |
| [#2044](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2044) | 2024-10-25 | Avoid allocating an `ImmutableArray<T>.Builder` during deserialization | 3 | 13 | - | ask | 93.5 | ask | mandate rule: source-without-tests; trust cap: build-config; trust cap: runtime-core; risk score: risk |
| [#2043](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2043) | 2024-10-25 | Allow SequencePool to Clear self | 5 | 13 | - | ask | 90.5 | ask | mandate rule: public-api-change; mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2045](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2045) | 2024-10-29 | Revert untrusted data default | 5 | 29 | - | ask | 86.2 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#1986](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1986) | 2024-11-07 | Add `MessagePackPrimitives` class | 16 | 5070 | - | block | 146.2 | block | risk score: risk |
| [#2056](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2056) | 2024-11-09 | Fix an issue about comparing generic type parameter constraints | 5 | 267 | - | notify | 30.6 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2057](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2057) | 2024-11-09 | Fix issues about code analysis and code fix of MsgPack003 | 2 | 274 | - | notify | 33.0 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2061](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2061) | 2024-11-11 | Fix serializing BigInteger and Decimal | 2 | 21 | - | ask | 62.8 | ask | trust cap: runtime-core; risk score: risk |
| [#2063](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2063) | 2024-11-12 | SequencePool support MemoryPool. | 5 | 29 | - | ask | 91.2 | ask | mandate rule: public-api-change; mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2059](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2059) | 2024-11-12 | Fix issues about Memory/ReadOnlyMemory/ReadOnlySequence in Source Gene | 10 | 694 | - | notify | 39.2 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2070](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2070) | 2024-11-19 | Fix bugs for Hardware Intrinsics | 2 | 26 | - | ask | 63.0 | ask | trust cap: runtime-core; risk score: risk |
| [#2073](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2073) | 2024-12-03 | Set MaximumObjectGraphDepth to TrustedData | 1 | 6 | - | ask | 111.2 | ask | mandate rule: public-api-change; mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2090](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2090) | 2024-12-11 | Add .NET 9 | 47 | 3212 | - | ask | 120.0 | block | mandate rule: public-api-change; mandate rule: dependency-check-failed; trust cap: build-config; trust cap: runtime-core; trust cap: unmapped; risk score: risk |
| [#2093](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2093) | 2024-12-12 | Check IsGenericType before call ConstructUnboundGenericType() | 3 | 14 | - | ask | 53.6 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#2094](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2094) | 2024-12-12 | Remove NerdBank.GitVersioning | 10 | 95 | - | ask | 33.8 | ask | trust cap: build-config; trust cap: unmapped |
| [#2095](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2095) | 2024-12-12 | Current all apis to shipped.txt | 12 | 1421 | - | block | 142.0 | block | risk score: risk |
| [#2105](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2105) | 2024-12-25 | allow DynamicGenericResolver to StandardResolver in DynamicAssembly.Av | 1 | 2 | - | ask | 66.1 | ask | mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2103](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2103) | 2024-12-25 | Fix source generator, don't generate when abstract/interface is not un | 5 | 895 | - | ask | 45.0 | ask | risk score: risk |
| [#2106](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2106) | 2024-12-26 | enable analyze union / stop collect field when object marked SuppressS | 9 | 530 | - | notify | 37.3 | ask | trust cap: generator-analyzer-core; risk score: risk |
| [#2123](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2123) | 2025-01-09 | Add missing recursion guard to `CodeAnalysisUtilities.GetTypeParameter | 1 | 2 | - | ask | 51.1 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#2135](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2135) | 2025-01-23 | Fix issues about Double.MaxValue | 1 | 4 | - | ask | 66.2 | ask | mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2119](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2119) | 2025-01-27 | Consolidation of AssemblyBuilderAccess when generating dynamic assembl | 1 | 6 | - | ask | 91.2 | ask | mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2134](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2134) | 2025-01-27 | Protects the generated resolver type metadata from trimmer | 2 | 305 | - | ask | 124.2 | ask | mandate rule: public-api-change; mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2136](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2136) | 2025-01-27 | Add PreserveAttribute to generic formatters for Unity IL2CPP | 15 | 143 | - | ask | 110.2 | ask | mandate rule: source-without-tests; trust cap: runtime-core; trust cap: unmapped; risk score: risk |
| [#2139](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2139) | 2025-01-27 | Change ByteListFormatter behaviour to keep binary compatibility for Li | 5 | 232 | - | ask | 91.2 | ask | mandate rule: public-api-change; trust cap: runtime-core; risk score: risk |
| [#2150](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2150) | 2025-02-04 | Fix stackoverflow on analyzer | 4 | 21 | - | ask | 54.8 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#2153](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2153) | 2025-02-09 | Fix SkipClrVisibilityChecks to notice private fields in base classes | 2 | 99 | - | ask | 41.0 | ask | trust cap: runtime-core; risk score: risk |
| [#2172](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2172) | 2025-03-04 | Add memory size check to `GetMemoryCheckResult` | 1 | 14 | - | ask | 66.6 | ask | mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2185](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2185) | 2025-06-06 | AccessModifier was added to generated code. | 126 | 251 | - | block | 80.0 | block | mandate rule: split-large-change |
| [#2206](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2206) | 2025-08-17 | Remove unneeded GetTypeInfo() calls | 19 | 382 | - | block | 144.3 | block | risk score: risk |
| [#2212](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2212) | 2025-08-17 | Use 'Write' instead of 'WriteInt32' for union type keys | 5 | 10 | - | ask | 55.5 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#2225](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2225) | 2025-08-22 | Fix Incorrect DateTimeOffset Serializer | 1 | 2 | yes (high) | ask | 91.1 | ask | mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2224](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2224) | 2025-08-22 | Fix various disposable issues | 4 | 33 | - | ask | 95.3 | ask | mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2226](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2226) | 2025-08-31 | fix: prevent StackOverflow in Equals with recursive generic constraint | 1 | 6 | - | ask | 51.2 | ask | mandate rule: source-without-tests; mandate rule: mandated-check-missing; risk score: risk |
| [#2235](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2235) | 2026-02-27 | Fix LICENSE notices for BufferWriter.cs | 2 | 20 | - | ask | 67.8 | ask | mandate rule: source-without-tests; trust cap: runtime-core; trust cap: unmapped; risk score: risk |
| [#2260](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2260) | 2026-05-13 | Fix typo and ignore .lscache files | 2 | 4 | - | ask | 92.2 | ask | mandate rule: source-without-tests; trust cap: runtime-core; trust cap: unmapped; risk score: risk |
| [#2256](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2256) | 2026-05-14 | Add more types to the default disallow list of named types to be deser | 1 | 6 | - | ask | 66.2 | ask | mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2262](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2262) | 2026-05-15 | Revert DateTimeOffset encoding change | 2 | 29 | - | ask | 63.2 | ask | trust cap: runtime-core; risk score: risk |
| [#2270](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2270) | 2026-05-21 | Add several known unsafe 'gadgets' to the disallow list | 1 | 11 | - | ask | 66.4 | ask | mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2271](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2271) | 2026-06-01 | Add `scoped` to `MessagePackWriter.Write(ReadOnlySpan<T>)` methods | 1 | 4 | - | ask | 86.2 | ask | mandate rule: public-api-change; mandate rule: source-without-tests; trust cap: runtime-core; risk score: risk |
| [#2275](https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2275) | 2026-06-09 | Fix security issues in develop | 33 | 1557 | - | ask | 120.1 | block | mandate rule: public-api-change; trust cap: runtime-core; trust cap: security-tests; trust cap: unmapped; risk score: risk |

## Regressions we could not attribute to one PR in the set

- #2101: 3.1.0 broke TypelessObjectResolver (fixed by #2103) (regression between 3.0.308 and 3.1.0; SZZ only finds adjacent lines from #1736)
- #2209: 3.1 regression with chained polymorphic types (no fix PR merged; cause not identified)
- #2046: MsgPack003 analysis/code fix broken for Nullable and generics in 3.0 (fixed by #2057) (origin is #1599 (May 2023), before the set)
