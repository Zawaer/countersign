// Copyright (c) All contributors. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

using MessagePack.SourceGenerator.Analyzers;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.Diagnostics;

/// <summary>
/// Countersign executable repro for reviewer finding claude/C2 on change 2234 (evidence/repros/2234/C2), the basis of
/// claude's REQ-2234-N1 "not_met" verdict.
/// </summary>
/// <remarks>
/// Claim: with <c>SuppressSourceGeneration = true</c>, a positional record whose property has <c>[property: Key(null)]</c>
/// still crashes the analyzer (AD0001 InvalidCastException): the BothStringAndIntKeyAreNull path hard-casts the property's
/// syntax to PropertyDeclarationSyntax, but for a positional record it is a ParameterSyntax. The change did not touch that
/// line, so REQ-2234-N1 ("must not crash on invalid contracts ... in such types") is not fully met.
/// The test states the required behaviour (no analyzer crash), so it is expected to FAIL on the change's head, and also on
/// base (the crash predates the change; the change leaves it in place).
/// </remarks>
public class ReproClaude2234C2Tests
{
    private const string AppSource = """
using MessagePack;

namespace App
{
    [MessagePackObject(SuppressSourceGeneration = true)]
    public record Cmd([property: Key(null)] string Scope);
}
""";

    [Fact]
    public async Task PositionalRecordWithNullKeyDoesNotCrashAnalyzerForSuppressedType()
    {
        (ImmutableArray<Diagnostic> diagnostics, IReadOnlyList<Exception> crashes) = await RunAnalyzerAsync("App", AppSource);
        string seen = Describe(diagnostics);

        Assert.True(crashes.Count == 0, "analyzer crashed: " + string.Join("; ", crashes.Select(e => e.GetType().Name + ": " + e.Message)) + " | " + seen);
        Assert.True(!diagnostics.Any(d => d.Id == "AD0001"), "analyzer crashed (AD0001): " + seen);
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
