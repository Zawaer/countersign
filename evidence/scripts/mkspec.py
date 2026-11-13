import json
SGP='tests/MessagePack.SourceGenerator.Tests'
F='src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs'
EXEC_REASON=("SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator "
  "(warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile "
  "(CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. "
  "Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.")
def exec_check(n, cls):
    return {'id':'tests.targeted.execution','tool':'dotnet build/test tests/MessagePack.SourceGenerator.ExecutionTests','tool_version':'8.0.402','status':'error',
            'summary':f'could not run {cls}: ExecutionTests project does not compile with SDK 8.0.402 (generator needs Roslyn 4.12; CS9057). Same failure on base.',
            'reason':EXEC_REASON,'log':f'evidence/{n}/logs/execution_tests.build.log'}
common_not_run=[
  {'id':'tests.execution','reason':EXEC_REASON},
  {'id':'tests.MessagePack.Tests','reason':'runtime library src/MessagePack not modified by the change; suite not run'},
  {'id':'build.net472/netstandard','reason':'only the net8.0 slice of src/MessagePack was built (Linux container, Debug)'},
  {'id':'benchmarks','reason':'no runtime serialization hot path touched (generator/analyzer only)'},
]
def pa(status, summary, **kw):
    d={'id':'public_api','tool':'git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/','status':status,'summary':summary}; d.update(kw); return d
pa_none=pa('pass','no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/', publicapi_files_changed=[])
def mut(m, desc, expect):
    j=json.load(open(f'/data/work/{m}.json'))
    return {'file':F,'line':j['line'],'before':j['before'].strip(),'after':j['after'].strip(),'description':desc,'intended_effect':expect}
changes=[
 {'change':'2283','label':'2283','filters':['FullyQualifiedName~GenericsFormatterTests.'],'fwf':'2283-fwf','reverted':[F],'public_api':pa_none,
  'not_run':common_not_run},
 {'change':'2234','label':'2234','filters':['FullyQualifiedName~SuppressSourceGenerationAnalyzerTests.'],'fwf':'2234-fwf','reverted':[F],'public_api':pa_none,
  'extra_checks':[exec_check('2234','SuppressedSourceGenerationTests (2 new tests: NoFormatterIsGeneratedForSuppressedType, SuppressedTypeRoundTripsThroughDynamicResolver)')],
  'not_run':common_not_run},
 {'change':'2297','label':'2297','filters':['FullyQualifiedName~CodeCoverageExclusionTests.'],'fwf':'2297-fwf',
  'reverted':['src/MessagePack.SourceGenerator/Transforms/*Template.{tt,cs}','src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs (13 files)'],'public_api':pa_none,
  'not_run':common_not_run},
 {'change':'2129','label':'2129','filters':['FullyQualifiedName~GeneratedMessagePackFormatterTests.'],
  'fwf':'2129-fwf','reverted':['all 13 files under src/ changed by the branch (2 added files deleted, 11 restored to base), including src/MessagePack.Annotations/Attributes.cs'],
  'public_api':pa('fail','public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md',
     publicapi_files_changed=[], added_public_declarations=['src/MessagePack.Annotations/Attributes.cs: public class GeneratedMessagePackFormatterAttribute : Attribute','src/MessagePack.Annotations/Attributes.cs: public Type? SurrogateType { get; set; }','src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs: public const string / public static readonly DiagnosticDescriptor for MsgPack019, MsgPack020, MsgPack021, MsgPack022','src/MessagePack.SourceGenerator/CodeAnalysis/GeneratedFormatterRequest.cs: public sealed record GeneratedFormatterRequest','src/MessagePack.SourceGenerator/CodeAnalysis/ObjectSerializationInfo.cs: public bool IsUserDeclaredFormatter'],
     untracked_projects=['src/MessagePack.Annotations (no PublicAPI.Shipped.txt/Unshipped.txt)']),
  'extra_checks':[exec_check('2129','GeneratedFormatterForExternalTypesTests (the runtime round-trip tests for the feature)'),
     {'id':'solution_membership','tool':'grep MessagePack.sln','status':'fail','summary':'new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced from ExecutionTests.csproj)'}],
  'not_run':common_not_run},
 {'change':'2283-mut1','label':'2283-mut1','filters':['FullyQualifiedName~GenericsFormatterTests.'],'mutation':mut('2283-mut1','remove the ContainsSyntaxTree guard in ReportIfLocatedInCompilation, so in-source diagnostics located in another compilation\'s syntax tree are reported again','REQ-2283-F3: a type from a project reference (CompilationReference, e.g. IDE/project-to-project) has source locations outside the analyzed compilation; reporting there makes Roslyn throw (AD0001)'),
  'not_run':[{'id':'public_api','reason':'mutant run: only build + targeted tests (+ full suite recorded as extra check)'},{'id':'analyzers','reason':'mutant run'}]},
 {'change':'2283-mut2','label':'2283-mut2','filters':['FullyQualifiedName~GenericsFormatterTests.'],'mutation':mut('2283-mut2','reintroduce the unguarded DeclaringSyntaxReferences[0] index for the MemberNeedsKey (MsgPack004) location','metadata-only member has no syntax reference -> IndexOutOfRangeException in generator/analyzer (CS8785/AD0001), REQ-2283-F1/F2'),
  'not_run':[{'id':'public_api','reason':'mutant run'},{'id':'analyzers','reason':'mutant run'}]},
 {'change':'2234-mut1','label':'2234-mut1','filters':['FullyQualifiedName~SuppressSourceGenerationAnalyzerTests.'],'mutation':mut('2234-mut1','remove the ContainsKey guard before intMembers.Add in the property loop','duplicate [Key(n)] on properties -> Dictionary.Add throws ArgumentException -> analyzer crash, MsgPack005 lost (REQ-2234-N1)'),
  'not_run':[{'id':'public_api','reason':'mutant run'},{'id':'analyzers','reason':'mutant run'}]},
 {'change':'2234-mut2','label':'2234-mut2','filters':['FullyQualifiedName~SuppressSourceGenerationAnalyzerTests.'],'mutation':mut('2234-mut2','drop the `continue` after DoNotMixStringAndIntKeys in the FIELD loop','fields with mixed int/string keys -> falls through to intKey!.Value on a null key -> InvalidOperationException -> analyzer crash (REQ-2234-N1, fields)'),
  'not_run':[{'id':'public_api','reason':'mutant run'},{'id':'analyzers','reason':'mutant run'}]},
]
json.dump({'changes':changes},open('/data/work/scripts/spec.json','w'),indent=1)
