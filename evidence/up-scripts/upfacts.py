#!/usr/bin/env python3
"""Stage-1 facts for merged upstream MessagePack-CSharp PRs used as low-risk controls (evidence/up-<pr>/facts.json).

Reuses evidence/scripts/facts.py (diff kinds, TRX parsing, build/targeted/full-suite/fail-without-fix logic) unchanged;
only the base, head and raw-output folder differ per PR. Each PR: base = merge commit's first parent, head = its second
parent (the PR branch tip; for all three, git diff base..head == git diff base..merge).

Raw runs (evidence/scripts/run.sh with WORK=/data/work/up/<pr>, SDK 8.0.402, -m:8, MaxCpuCount=8):
  up-2022  base f5e104ee, head 5f4b762a, fwf = head with src/ reverted to base; filter MsgPack00xAnalyzerTests.; full suite on all three
  up-1934  base 7ef21d4b, head 2f9324f9 (test-only, so no fail-without-fix); plus pre1926 = 3ea9234f (before the #1926 fix
           this PR follows up) and pre1926-newtests = 3ea9234f + this PR's diff, to see whether the new test settings
           detect the #1925 regression. global.json pins 8.0.300 (rollForward patch) at these commits; only 8.0.402 is
           installed, so global.json was set to 8.0.402 in the scratch worktrees only, and restored afterwards.
  up-1967  docs only: nothing built; README anchors checked by docs_anchors() below.
  demo-docs1  agent-written docs-only fix in the demo repo (Zawaer/countersign-messagepack-demo, branch ju26-demo-docs1,
           base 32258fdb): same docs checks as up-1967, plus injection_scan (it is agent-written, so it gets a PR).
Usage: python3 -I evidence/up-scripts/upfacts.py [up-2022 up-1934 up-1967]
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.dirname(HERE)
os.environ.setdefault('CS_SRC', '/data/src')
os.environ.setdefault('CS_EVID', EVID)
spec = importlib.util.spec_from_file_location('csfacts', os.path.join(EVID, 'scripts', 'facts.py'))
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
UP = 'https://github.com/MessagePack-CSharp/MessagePack-CSharp'
SG = F.SG
SDK_NOTE_1934 = ('global.json at these commits pins SDK 8.0.300 with rollForward patch; only 8.0.402 is installed, so global.json '
                 'was set to 8.0.402 (rollForward disable) in the scratch worktrees only and restored afterwards')
SDK_NOTE_2305 = ('global.json at upstream master (f2bfa97e) pins SDK 10.0.300; only 8.0.402 and 9.0.321 are installed, so global.json '
                 'was set to 9.0.321 (rollForward disable) in the scratch worktrees only (base, head, fwf); every project builds net8.0')

CHANGES = {
    'up-2022': dict(pr=2022, merge='e88df8a75dcfe186e31a9217192d93f667d720b8', issue=2017, kind='source fix + test',
                    filters=['FullyQualifiedName~MsgPack00xAnalyzerTests.'], fwf='fwf',
                    reverted=['src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs']),
    'up-1934': dict(pr=1934, merge='b06681eaafee88475f2b2c958397eb540dad9d0e', issue=1925, kind='test only',
                    filters=['FullyQualifiedName~CustomStringKeyFormatterTests.|FullyQualifiedName~GenerationTests.|'
                             'FullyQualifiedName~GenericsFormatterTests.|FullyQualifiedName~PrivateMemberAccessTests.'],
                    fwf=None, sdk_note=SDK_NOTE_1934),
    'up-1967': dict(pr=1967, merge='1d24c54a5049612cabf826e23582468bef96ff44', issue=None, kind='docs only'),
    # Not merged: an upstream community PR still open when we ran it (no merged fix exists for #2283 or #2234). There is no
    # merge commit, so base = merge-base of the PR head with upstream master, head = the PR head (fetched as refs/upstream/pr-2305).
    'up-2305': dict(pr=2305, base='f2bfa97ef56c3e0eda92d7df34856467afcda865', head='b08ebeeb7d77b7cca599cd7c91b2b1fbd9cfb3c4',
                    issue=2283, kind='source fix + test', state='open (not merged) when run, 2026-11-14',
                    filters=['FullyQualifiedName~GenericsFormatterTests.'], fwf='fwf',
                    reverted=['src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs'],
                    sdk='9.0.321', sdk_note=SDK_NOTE_2305),
    # Agent-written (not upstream): the first change meant to clear through the demo repo's PR gate. No PR number upstream.
    'demo-docs1': dict(base='32258fdbee4bcd653c79f51b4376b5103c6f4d27', head='6e9b25c578509b1b38d60d5c99f851ac4897e780',
                       kind='docs only', agent=True, branch='ju26-demo-docs1',
                       repo='https://github.com/Zawaer/countersign-messagepack-demo'),
}


def git(*a):
    return F.git(*a)


def slug(heading):
    s = re.sub(r'</?a\b[^>]*>', '', heading).strip().lower()  # drop <a name=..> tags, keep text such as <T>
    s = re.sub(r'[^\w\- ]', '', s)
    return s.replace(' ', '-')


def anchors_of(text):
    names = set(re.findall(r'<a\s+(?:name|id)="([^"]+)"', text))
    seen = {}
    for line in text.splitlines():
        m = re.match(r'#{1,6}\s+(.*)', line)
        if m:
            s = slug(m.group(1))
            n = seen.get(s, 0)
            seen[s] = n + 1
            names.add(s if n == 0 else f'{s}-{n}')
    return names


def links_of(text):
    return [(i + 1, m.group(1)) for i, l in enumerate(text.splitlines()) for m in re.finditer(r'\]\(#([^)\s]+)\)', l)]


def added_lines(base, head, path):
    """Line numbers (at head) of lines the change added or modified in `path`."""
    out = set()
    for h in re.finditer(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', git('diff', '-U0', base, head, '--', path), re.M):
        start, cnt = int(h.group(1)), int(h.group(2) or 1)
        out |= set(range(start, start + cnt))
    return out


def docs_anchors(base, head, md_files):
    """Intra-document links ](#x) must resolve to an <a name/id> or a GitHub heading slug.
    Status is about the lines the change added or modified (like tests.full_suite judges failures not on base);
    unresolved links on untouched lines are reported, not counted against the change."""
    per, touched = [], []
    for p in md_files:
        h, b = git('show', f'{head}:{p}'), git('show', f'{base}:{p}')
        ha, ba = anchors_of(h), anchors_of(b)
        hl, bl = links_of(h), links_of(b)
        mine = added_lines(base, head, p)
        for n, a in hl:
            if n in mine:
                touched.append({'file': p, 'line': n, 'anchor': a, 'resolves_at_head': a in ha})
        unres_h = sorted({a for n, a in hl if a not in ha and n not in mine})
        per.append({'file': p, 'links_at_head': len(hl), 'links_at_base': len(bl),
                    'unresolved_at_base': sorted({a for _, a in bl if a not in ba}),
                    'unresolved_at_head_on_untouched_lines': unres_h})
    bad = [t for t in touched if not t['resolves_at_head']]
    st = 'pass' if touched and not bad else ('fail' if bad else 'skipped')
    summ = (f"{len(touched)} intra-document link(s) on lines the change touched, {len(bad)} unresolved at head; "
            + '; '.join(f"{f['file']}: base had {len(f['unresolved_at_base'])} unresolved of {f['links_at_base']}, "
                        f"head has {len(f['unresolved_at_head_on_untouched_lines'])} unresolved on lines the change did not touch "
                        f"({', '.join('#' + x for x in f['unresolved_at_head_on_untouched_lines'])})" for f in per))
    return {'id': 'docs.anchors', 'tool': 'evidence/up-scripts/upfacts.py docs_anchors (GitHub heading slugs + <a name/id>)',
            'status': st, 'summary': summ, 'links_on_touched_lines': touched, 'files': per}


def skipped(id_, reason):
    return {'id': id_, 'status': 'skipped', 'summary': f'not run: {reason}', 'reason': reason}


def main(argv):
    for n in argv or list(CHANGES):
        c = CHANGES[n]
        merge = c.get('merge')
        if merge:
            base, head = git('rev-parse', merge + '^1').strip(), git('rev-parse', merge + '^2').strip()
            assert git('diff', base, head) == git('diff', base, merge), 'base..head differs from base..merge'
        else:  # open PR or agent branch: no merge commit
            base, head = c['base'], c['head']
            assert git('merge-base', base, head).strip() == base, 'base is not the merge-base of the PR head'
        F.BASE = base
        F._tt_cache.clear()
        F.OUT = f'/data/work/up/{c.get("pr") or n}/out'
        cd = os.path.join(EVID, n)
        os.makedirs(cd, exist_ok=True)
        diff = F.diff_facts(head)
        newset = F.new_tests(head)
        if c.get('agent'):
            facts = {'change': n, 'branch': c['branch'], 'base': base[:8], 'head': head[:8], 'base_full': base, 'head_full': head,
                     'commit_message': git('log', '-1', '--format=%B', head).strip(), 'author': git('log', '-1', '--format=%an', head).strip(),
                     'agent_written': True, 'repo': c['repo'], 'diff': diff, 'new_tests_in_diff': sorted(newset)}
        else:
            facts = {'change': n, 'branch': f'upstream PR #{c["pr"]}', 'base': base[:8], 'head': head[:8], 'base_full': base, 'head_full': head,
                   'commit_message': git('log', '-1', '--format=%B', head).strip(), 'author': git('log', '-1', '--format=%an', head).strip(),
                   'agent_written': False,
                   'upstream': ({'pull_request': f'{UP}/pull/{c["pr"]}', 'issue': f'{UP}/issues/{c["issue"]}' if c['issue'] else None,
                                 'merge_commit': merge, 'merged_into': 'develop', 'merged_at': git('log', '-1', '--format=%cI', merge).strip(),
                                 'base_rule': 'base = merge commit first parent (develop before the merge)',
                                 'head_rule': 'head = merge commit second parent (PR branch tip); git diff base..head == git diff base..merge (asserted)',
                                 'control': f'{c["kind"]}; merged upstream, human-written, not reverted or fixed later as far as checked '
                                            '(measurement/history/candidates.json has no entry for it; later history of the changed lines read by hand)'}
                                if merge else
                                {'pull_request': f'{UP}/pull/{c["pr"]}', 'issue': f'{UP}/issues/{c["issue"]}', 'state': c['state'],
                                 'merge_commit': None, 'base_rule': 'base = merge-base of the PR head with upstream master (asserted)',
                                 'head_rule': 'head = PR head commit (refs/pull/<pr>/head)',
                                 'benchmark': f'{c["kind"]}; a fix for the same issue as the agent-written change, written by an upstream '
                                              'contributor (whether tools helped is not known); not reviewed or merged upstream, so not a control'}),
                   'diff': diff, 'new_tests_in_diff': sorted(newset)}
        checks, not_run = [], []
        if c['kind'] == 'docs only':
            r = 'docs-only change: no compiled or test file changed (only README.md), so nothing was built or run'
            checks += [skipped('build', r), skipped('tests.targeted', r), skipped('tests.fail_without_fix', r), skipped('tests.full_suite', r)]
            checks.append({'id': 'public_api', 'tool': 'git diff --name-only (no file under src/ changed)', 'status': 'pass',
                           'summary': 'no public API changes: the change touches no file under src/ and no PublicAPI.*.txt', 'publicapi_files_changed': []})
            checks.append(skipped('analyzers', r))
            checks.append(docs_anchors(base, head, [f['path'] for f in diff['by_file'] if f['path'].endswith('.md')]))
            not_run = [{'id': 'docs.rendering', 'reason': 'Markdown was not rendered; anchors were resolved with GitHub slug rules re-implemented in upfacts.py'},
                       {'id': 'docs.external_links', 'reason': 'links to other files or URLs were not followed (offline)'}]
            env = {'os': F.OS_DESC, 'note': 'no .NET build for a docs-only change'}
        else:
            meta = F.read_meta('head')
            base_full = F.parse_trx(os.path.join(F.OUT, 'base', 'full.trx')) or []
            base_fail = {t['name'] for t in base_full if t['outcome'] == 'failed'}
            base_warn = F.warnings('base')
            b, wl = F.build_check('head', cd, meta)
            if c.get('sdk_note'):
                b['tool_version_note'] = c['sdk_note']
            checks.append(b)
            t = F.targeted_check('head', cd, meta, newset)
            t['filter'], t['project'] = c['filters'], SG
            bm = F.read_meta('base')
            if bm and 'targeted_1_rc' in bm:
                bt = F.parse_trx(os.path.join(F.OUT, 'base', 'targeted.1.trx')) or []
                t['on_base'] = f'same filter on base: {sum(x["outcome"] == "passed" for x in bt)} passed, {sum(x["outcome"] == "failed" for x in bt)} failed of {len(bt)}'
            checks.append(t)
            if c['fwf']:
                fm = F.read_meta(c['fwf'])
                fw = F.targeted_check(c['fwf'], cd, fm, newset, id_='tests.fail_without_fix', tool='dotnet test (source reverted, tests kept)')
                newt = [x for x in fw['tests'] if x['new']]
                nf = sum(x['outcome'] == 'failed' for x in newt)
                fw['reverted_files'] = c['reverted']
                ff = F.parse_trx(os.path.join(F.OUT, c['fwf'], 'full.trx'))
                if ff is not None:
                    F.copy_log(os.path.join(F.OUT, c['fwf'], 'full.log'), os.path.join(cd, 'logs', 'fail_without_fix.full_suite.log'))
                    fl = [x['name'] for x in ff if x['outcome'] == 'failed']
                    fw['full_suite_with_source_reverted'] = {'total': len(ff), 'failed': len(fl), 'failed_tests': fl,
                                                             'log': f'evidence/{n}/logs/fail_without_fix.full_suite.log'}
                fw['new_failed'], fw['new_total'] = nf, len(newt)
                fw['status'] = 'pass' if nf else 'fail'
                fw['summary'] = (f'new tests fail on base source: {nf}/{len(newt)} failed -> tests do cover the change' if nf
                                 else f'new tests pass on base source: 0/{len(newt)} failed -> tests do NOT demonstrate the change')
                checks.append(fw)
            else:
                checks.append(skipped('tests.fail_without_fix', 'test-only change: no file under src/ changed, so there is no source to revert '
                                      '(see tests.detects_original_regression for what the new test settings catch)'))
            fc = F.full_check('head', cd, meta, base_fail)
            fc['base_total'], fc['base_passed'] = len(base_full), sum(x['outcome'] == 'passed' for x in base_full)
            checks.append(fc)
            checks.append({'id': 'public_api', 'tool': 'git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/', 'status': 'pass',
                           'summary': 'no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/',
                           'publicapi_files_changed': []})
            newwarn, gone = sorted(set(wl) - base_warn), sorted(base_warn - set(wl))
            checks.append({'id': 'analyzers', 'tool': 'dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base',
                           'status': 'pass' if not newwarn else 'fail', 'summary': 'no new warnings' if not newwarn else f'{len(newwarn)} new warnings vs base',
                           'new_warnings': newwarn, 'resolved_warnings': gone, 'base_warning_count': len(base_warn)})
            if n == 'up-1934':
                checks.append(regression_check(cd))
            not_run = [{'id': 'tests.MessagePack.Tests', 'reason': 'runtime library src/MessagePack not modified by the change; suite not run'},
                       {'id': 'tests.execution', 'reason': 'ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite)'},
                       {'id': 'build.net472/netstandard', 'reason': 'only the net8.0 slice of src/MessagePack was built (Linux container, Debug)'},
                       {'id': 'benchmarks', 'reason': 'no runtime serialization hot path touched'}]
            if c.get('sdk'):
                for x in checks:
                    if x.get('tool_version') == F.SDK:
                        x['tool_version'] = c['sdk']
            env = {'sdk': c.get('sdk', F.SDK), 'os': F.OS_DESC, 'configuration': 'Debug', 'max_cpu': 8, **({'sdk_note': c['sdk_note']} if c.get('sdk_note') else {})}
        if c.get('agent'):  # agent-written: scan the diff, branch and commit message for text planted for reviewers
            checks.append(F.injection_check(facts))
        facts['checks'], facts['not_run'], facts['environment'] = checks, not_run, env
        json.dump(facts, open(os.path.join(cd, 'facts.json'), 'w'), indent=2)
        print(n, [(x['id'], x['status']) for x in checks])


def regression_check(cd):
    """up-1934: the PR's test changes on top of the source *before* #1926 (which fixed #1925, generated code needing C# 8/9).
    Tests that fail there but pass with the old test files are the ones the new C# 7.3 default makes sensitive to #1925."""
    old = F.parse_trx(os.path.join(F.OUT, 'pre1926', 'full.trx')) or []
    new = F.parse_trx(os.path.join(F.OUT, 'pre1926-newtests', 'full.trx')) or []
    F.copy_log(os.path.join(F.OUT, 'pre1926-newtests', 'full.log'), os.path.join(cd, 'logs', 'detects_original_regression.newtests.log'))
    F.copy_log(os.path.join(F.OUT, 'pre1926', 'full.log'), os.path.join(cd, 'logs', 'detects_original_regression.oldtests.log'))
    oldo = {t['name']: t['outcome'] for t in old}
    caught = [t for t in new if t['outcome'] == 'failed' and oldo.get(t['name']) == 'passed']
    both = [t['name'] for t in new if t['outcome'] == 'failed' and oldo.get(t['name']) == 'failed']
    st = 'error' if not old or not new else ('pass' if caught else 'fail')
    return {'id': 'tests.detects_original_regression', 'tool': 'dotnet test (full SourceGenerator.Tests) on source before the #1926 fix, old vs new test files',
            'tool_version': F.SDK, 'tool_version_note': SDK_NOTE_1934, 'status': st,
            'setup': 'pre1926 = commit 3ea9234f (merge^1 of #1926, i.e. generator still emitting C# 8/9 syntax, issue #1925) with its own tests; '
                     'pre1926-newtests = 3ea9234f + git diff 7ef21d4b..2f9324f9 (this PR, test files only; applies cleanly)',
            'summary': (f'with this PR\'s test changes, {len(caught)} tests fail on the pre-#1926 generator that pass with the old test files '
                        f'-> the new C# 7.3 default detects the #1925 regression' if caught else 'no test changes outcome -> the new settings do not detect #1925')
                       + f' (old tests: {sum(o == "failed" for o in oldo.values())}/{len(old)} failed; new tests: {sum(t["outcome"] == "failed" for t in new)}/{len(new)} failed; '
                         f'{len(both)} fail either way)',
            'tests': [{'name': t['name'], 'outcome': 'failed', 'outcome_with_old_tests': 'passed', 'error': (t['error'] or '')[:400]} for t in caught],
            'failed_either_way': both,
            'log': [f'evidence/{os.path.basename(cd)}/logs/detects_original_regression.newtests.log', f'evidence/{os.path.basename(cd)}/logs/detects_original_regression.oldtests.log']}


if __name__ == '__main__':
    main(sys.argv[1:])
