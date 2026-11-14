// Copyright (c) All contributors. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

using MessagePack.SourceGenerator.Analyzers;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.Diagnostics;

/// <summary>
/// Countersign executable repro for reviewer finding claude/C1 on change 2283 (evidence/repros/2283/C1).
/// </summary>
/// <remarks>
/// Claim: the change's new location filter (ReportIfLocatedInCompilation) drops every diagnostic whose location is not in
/// the compilation's own source. When a generic class from a referenced assembly is closed over an app type that lacks
/// [MessagePackObject] (Lib.Item&lt;App.Foo&gt;), MsgPack003 about App.Foo is located on the metadata member Item.Content,
/// so the change drops it: base reports MsgPack003, head reports nothing (a regression; this configuration did not crash on base).
/// The test states the behaviour the requirement asks for (REQ-2283-N1: existing diagnostics for types in the current
/// compilation keep working), so it is expected to FAIL on the change's head and PASS on base.
/// </remarks>
public class ReproClaude2283C1Tests
{
    private const string LibrarySource = """
using MessagePack;

namespace Lib
{
    [MessagePackObject]
    public class Item<T>
    {
        [Key(0)]
        public T Content { get; set; }
    }
}
""";

    private const string AppSource = """
using MessagePack;

namespace App
{
    public class Foo
    {
        public int X { get; set; }
    }

    [MessagePackObject]
    public class R
    {
        [Key(0)]
        public Lib.Item<Foo> Member { get; set; }
    }
}
""";

    [Fact]
    public async Task MsgPack003IsReportedForAppTypeArgumentOfGenericFromReferencedAssembly()
    {
        MetadataReference library = await CompileToMetadataReferenceAsync("Lib", LibrarySource);
        (ImmutableArray<Diagnostic> diagnostics, IReadOnlyList<Exception> crashes) = await RunAnalyzerAsync("App", AppSource, library);
        string seen = Describe(diagnostics);

        Assert.True(crashes.Count == 0 && !diagnostics.Any(d => d.Id == "AD0001"), "analyzer crashed: " + string.Join("; ", crashes.Select(e => e.GetType().Name + ": " + e.Message)) + " | " + seen);
        Assert.True(
            diagnostics.Any(d => d.Id == MsgPack00xMessagePackAnalyzer.UseMessagePackObjectAttributeId),
            "expected MsgPack003 (App.Foo is used through Lib.Item<Foo>.Content but lacks [MessagePackObject]); analyzer reported: " + seen);
    }

    private static string Describe(ImmutableArray<Diagnostic> diagnostics)
        => diagnostics.IsEmpty ? "(no diagnostics)" : string.Join(" | ", diagnostics.Select(d => $"{d.Id} at {(d.Location.IsInSource ? "source" : d.Location.Kind.ToString())}: {d.GetMessage()}"));

    private static async Task<(ImmutableArray<Diagnostic> Diagnostics, IReadOnlyList<Exception> Crashes)> RunAnalyzerAsync(string assemblyName, string source, params MetadataReference[] references)
    {
        Compilation compilation = await CreateCompilationAsync(assemblyName, source, references);
        var crashes = new List<Exception>();
        var options = new CompilationWithAnalyzersOptions(
            new Microsoft.CodeAnalysis.Diagnostics.AnalyzerOptions(ImmutableArray<AdditionalText>.Empty),
            (exception, analyzer, diagnostic) => crashes.Add(exception),
            concurrentAnalysis: false,
            logAnalyzerExecutionTime: false);
        ImmutableArray<Diagnostic> diagnostics = await compilation
            .WithAnalyzers(ImmutableArray.Create<DiagnosticAnalyzer>(new MsgPack00xMessagePackAnalyzer()), options)
            .GetAnalyzerDiagnosticsAsync();
        return (diagnostics, crashes);
    }

    private static async Task<MetadataReference> CompileToMetadataReferenceAsync(string assemblyName, string source)
    {
        Compilation compilation = await CreateCompilationAsync(assemblyName, source);
        using var stream = new MemoryStream();
        Microsoft.CodeAnalysis.Emit.EmitResult result = compilation.Emit(stream);
        Assert.True(result.Success, "referenced assembly did not compile: " + string.Join(Environment.NewLine, result.Diagnostics));
        return MetadataReference.CreateFromImage(stream.ToArray());
    }

    private static async Task<Compilation> CreateCompilationAsync(string assemblyName, string source, params MetadataReference[] references)
    {
        ImmutableArray<MetadataReference> framework = await ReferencesHelper.DefaultTargetFrameworkReferences.ResolveAsync(LanguageNames.CSharp, CancellationToken.None);
        Compilation compilation = CSharpCompilation.Create(
            assemblyName,
            new[] { CSharpSyntaxTree.ParseText(source, new CSharpParseOptions(LanguageVersion.CSharp10)) },
            framework.Concat(ReferencesHelper.GetReferences(ReferencesSet.MessagePack)).Concat(references),
            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
        Diagnostic[] errors = compilation.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error).ToArray();
        Assert.True(errors.Length == 0, "test source does not compile: " + string.Join(Environment.NewLine, errors.Select(e => e.ToString())));
        return compilation;
    }
}
