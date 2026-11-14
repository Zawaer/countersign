#!/usr/bin/env python3
"""Assemble Countersign stage-1 facts.json files from the raw run outputs in /data/work/out."""
import hashlib, json, os, re, shutil, subprocess, sys, xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))  # the countersign package (injection scanner) lives at the repo root

# Paths default to the original local run; CI (evidence/scripts/ci-facts.sh) overrides them with env vars.
SRC = os.environ.get('CS_SRC', '/data/src')
REPO = os.environ.get('CS_REPO', SRC + '/mp')
OUT = os.environ.get('CS_OUT', '/data/work/out')
EVID = os.environ.get('CS_EVID', '/data/worktrees/s_Vga5T2JJtb/evidence')
SPEC = os.environ.get('CS_SPEC', '/data/work/scripts/spec.json')
ONLY = os.environ.get('CS_ONLY')  # one change id: build facts for that change only
REPROS = os.environ.get('CS_REPROS', os.path.join(HERE, '..', 'repros'))  # evidence/repros/<change>/<finding>/repro.json
OS_DESC = os.environ.get('CS_OS_DESC', 'linux-x64 (container)')
WT_RE = re.escape(SRC) + r'/mp-[\w-]+/'
BASE = '32258fdbee4bcd653c79f51b4376b5103c6f4d27'
SDK = '8.0.402'
SG = 'tests/MessagePack.SourceGenerator.Tests'
NS = '{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}'
MAXLOG = 200_000


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True, check=True).stdout


# Folders of regenerated snapshots (the source generator's verified outputs): a change there is generated output by design.
SNAPSHOT_DIRS = ('tests/MessagePack.SourceGenerator.Tests/Resources/',)


def generator_input(p):
    """The input a generated-looking file is produced from: the T4 template next to a .cs, or None (no known input)."""
    return p[:-3] + '.tt' if p.endswith('.cs') and not p.endswith('.g.cs') else None


def counts_as_generated(p, changed):
    """A generated-looking file is `generated` only if it sits in a regenerated-snapshot folder or its input (the .tt)
    changed in the same diff. A hand edit to a template's output with the template untouched is a source change:
    reviewers see it and risk counts it (red team G2). `changed` = paths in the diff (None: unknown, so not trusted)."""
    if p.startswith(SNAPSHOT_DIRS):
        return True
    src = generator_input(p)
    return bool(src and changed is not None and src in changed)


def kind(path, changed=None):
    p = path
    if p.endswith('.g.cs') and counts_as_generated(p, changed):
        return 'generated'
    if p.endswith(('.md', '.txt')) and 'PublicAPI' not in p or p.startswith('doc/'):
        return 'build' if p.endswith('AnalyzerReleases.Unshipped.md') or p.endswith('AnalyzerReleases.Shipped.md') else 'doc'
    if p.endswith(('.csproj', '.props', '.targets', '.sln', '.json', '.yml', '.yaml')) or 'PublicAPI' in p:
        return 'build'
    if p.startswith('tests/'):
        return 'test'
    if (p.endswith('.cs') and (os.path.exists(os.path.join(REPO, p[:-3] + '.tt')) or git_has_tt(p))
            and counts_as_generated(p, changed)):
        return 'generated'
    return 'source'


_tt_cache = {}


def git_has_tt(p):
    # T4-generated .cs next to a .tt template (checked on the change head via ls-tree in the caller's rev)
    return _tt_cache.get(p[:-3] + '.tt', False)


def diff_facts(head):
    """Per-file insertions/deletions and kind. Binary files (numstat `-\t-`) are kind `binary` with 0/0 lines: git shows
    no lines for them, so nothing downstream (injection scan, reviewers) can read them."""
    changed = set(git('diff', '--name-only', BASE, head).splitlines())
    for f in git('ls-tree', '-r', '--name-only', head).splitlines():
        if f.endswith('.tt'):
            _tt_cache[f] = True
    by = []
    ins = dele = 0
    for line in git('diff', '--numstat', BASE, head).splitlines():
        a, d, p = line.split('\t', 2)
        if a == '-' and d == '-':
            by.append({'path': p, 'ins': 0, 'del': 0, 'kind': 'binary'})
            continue
        a, d = int(a), int(d)
        ins += a; dele += d
        by.append({'path': p, 'ins': a, 'del': d, 'kind': kind(p, changed)})
    counts = {}
    for f in by:
        counts[f['kind']] = counts.get(f['kind'], 0) + 1
    return {'files': len(by), 'insertions': ins, 'deletions': dele, 'by_kind': counts, 'by_file': by}


def read_meta(label):
    m = {}
    p = os.path.join(OUT, label, 'meta.txt')
    if not os.path.exists(p):
        return None
    for line in open(p):
        for tok in line.split():
            if '=' in tok:
                k, v = tok.split('=', 1)
                m[k] = v
    return m


def parse_trx(path):
    if not os.path.exists(path):
        return None
    root = ET.parse(path).getroot()
    res = []
    for r in root.iter(NS + 'UnitTestResult'):
        msg = r.find(f'{NS}Output/{NS}ErrorInfo/{NS}Message')
        res.append({'name': r.get('testName'), 'outcome': {'Passed': 'passed', 'Failed': 'failed', 'NotExecuted': 'skipped'}.get(r.get('outcome'), r.get('outcome').lower()),
                    'duration': r.get('duration'),
                    'error': (msg.text or '')[:1500] if msg is not None else None})
    res.sort(key=lambda x: x['name'])
    return res


def test_methods(rev, path):
    try:
        src = git('show', f'{rev}:{path}')
    except subprocess.CalledProcessError:
        return {}
    cls = None
    out = {}
    lines = src.splitlines()
    for i, l in enumerate(lines):
        m = re.match(r'\s*public\s+(?:sealed\s+|static\s+|partial\s+)*class\s+(\w+)', l)
        if m and (cls is None or (not cls.endswith('Tests') and m.group(1).endswith('Tests'))):
            cls = m.group(1)  # outer test class (prefer *Tests); later matches are usually inside test-source string literals
        m = re.match(r'\s*public\s+(?:async\s+)?(?:Task|void|ValueTask)\s+(\w+)\s*\(', l)
        if m and any(re.search(r'\[(Fact|Theory)', x) for x in lines[max(0, i - 4):i]):
            out[f'{cls}.{m.group(1)}'] = '\n'.join(lines[i:i + 60])
    return out


def new_tests(head):
    names = set()
    for p in git('diff', '--name-only', BASE, head, '--', 'tests').split():
        if not p.endswith('.cs') or p.endswith('.g.cs'):
            continue
        b, h = test_methods(BASE, p), test_methods(head, p)
        names |= set(h) - set(b)
    return names


def method_of(test_name):
    return test_name.split('(')[0]


def copy_log(src, dst):
    if not os.path.exists(src):
        return None
    data = open(src, 'rb').read()
    if len(data) > MAXLOG:
        data = data[:MAXLOG // 2] + b'\n\n[... trimmed ...]\n\n' + data[-MAXLOG // 2:]
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(data)
    return os.path.relpath(dst, os.path.dirname(EVID))


def warnings(label):
    ws = set()
    d = os.path.join(OUT, label)
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.startswith('build.warnings'):
            for l in open(os.path.join(d, f)):
                l = l.strip()
                if not l:
                    continue
                l = re.sub(WT_RE, '', l)
                l = re.sub(r'\(\d+,\d+(,\d+,\d+)?\)', '', l)
                ws.add(l)
    return ws


def build_check(label, change_dir, meta):
    log = copy_log(os.path.join(OUT, label, 'build.log'), os.path.join(change_dir, 'logs', 'build.log'))
    wl = sorted(warnings(label))
    if os.path.exists(os.path.join(OUT, label, 'build.warnings.1.log')):
        copy_log(os.path.join(OUT, label, 'build.warnings.1.log'), os.path.join(change_dir, 'logs', 'build.warnings.log'))
    blog = open(os.path.join(OUT, label, 'build.log')).read()
    errs = len(set(re.findall(r': error \w+:.*', blog)))
    ok = meta.get('build_rc') == '0'
    return {'id': 'build', 'tool': 'dotnet build', 'tool_version': SDK, 'status': 'pass' if ok else 'fail',
            'command': f'dotnet build {SG}/MessagePack.SourceGenerator.Tests.csproj --no-incremental -m:8 -c Debug',
            'projects': ['src/MessagePack.SourceGenerator', 'src/MessagePack.Analyzers.CodeFixes', 'src/MessagePack.Analyzers', 'src/MessagePack.Annotations', 'src/MessagePack (net8.0)', SG],
            'summary': f'{errs} errors, {len(wl)} unique warnings', 'log': log, 'duration_s': float(meta.get('build_s', 0))}, wl


def targeted_check(label, change_dir, meta, newset, id_='tests.targeted', tool='dotnet test'):
    tests = []
    logs = []
    filters = []
    j = 1
    dur = 0.0
    while f'targeted_{j}_rc' in meta:
        trx = parse_trx(os.path.join(OUT, label, f'targeted.{j}.trx')) or []
        filters.append(meta[f'targeted_{j}_filter'] if f'targeted_{j}_filter' in meta else None)
        dur += float(meta.get(f'targeted_{j}_s', 0))
        logs.append(copy_log(os.path.join(OUT, label, f'targeted.{j}.log'), os.path.join(change_dir, 'logs', f'{id_.replace(".", "_")}.{j}.log')))
        for t in trx:
            t2 = {'name': t['name'], 'outcome': t['outcome'], 'new': method_of(t['name']) in newset}
            if t['outcome'] == 'failed':
                t2['error'] = t['error']
            tests.append(t2)
        j += 1
    p = sum(t['outcome'] == 'passed' for t in tests)
    f = sum(t['outcome'] == 'failed' for t in tests)
    s = sum(t['outcome'] == 'skipped' for t in tests)
    n = sum(t['new'] for t in tests)
    status = 'error' if not tests else ('pass' if f == 0 else 'fail')
    return {'id': id_, 'tool': tool, 'tool_version': SDK, 'status': status,
            'summary': f'{p} passed, {f} failed, {s} skipped ({n} new tests in run)',
            'tests': tests, 'log': logs[0] if len(logs) == 1 else logs, 'duration_s': dur}


def full_check(label, change_dir, meta, base_fail):
    if 'full_rc' not in meta:
        return None
    trx = parse_trx(os.path.join(OUT, label, 'full.trx'))
    log = copy_log(os.path.join(OUT, label, 'full.log'), os.path.join(change_dir, 'logs', 'tests_full_suite.log'))
    if trx is None:
        return {'id': 'tests.full_suite', 'tool': 'dotnet test', 'status': 'error', 'summary': f'no results (rc={meta["full_rc"]})', 'log': log}
    failed = [t for t in trx if t['outcome'] == 'failed']
    newf = [t['name'] for t in failed if t['name'] not in base_fail]
    pre = [t['name'] for t in failed if t['name'] in base_fail]
    p = sum(t['outcome'] == 'passed' for t in trx)
    status = 'pass' if not newf else 'fail'
    summ = f'{SG}: {len(trx)} tests, {p} passed, {len(failed)} failed ({len(newf)} not failing on base, {len(pre)} also failing on base)'
    return {'id': 'tests.full_suite', 'tool': 'dotnet test', 'tool_version': SDK, 'status': status, 'summary': summ,
            'project': SG, 'total': len(trx), 'passed': p, 'failed': len(failed),
            'failures_not_on_base': [{'name': t['name'], 'error': t['error']} for t in failed if t['name'] not in base_fail],
            'failures_also_on_base': pre, 'log': log, 'duration_s': float(meta.get('full_s', 0))}


# ---- ExecutionTests / MapModeExecutionTests (SDK 9, scripts/exec9.sh -> /data/work/out/exec9-<label>) ----
SDK9 = os.environ.get('SDK9_VERSION', '9.0.321')
SDK9_NOTE = ('SDK 9 used because the generator needs Roslyn 4.12; repo pins 8.0.402 '
             f'(global.json overridden to {SDK9} in the scratch worktree only)')
EXEC_PROJS = ['ExecutionTests', 'MapModeExecutionTests']


def exec_proj(P):
    return f'tests/MessagePack.SourceGenerator.{P}'


def exec_run(label):
    """Parsed results of exec9.sh for one worktree label, or None if it was not run."""
    d = os.path.join(OUT, 'exec9-' + label)
    meta = read_meta('exec9-' + label)
    if meta is None or 'DONE' not in open(os.path.join(d, 'meta.txt')).read():
        return None
    r = {'meta': meta, 'dir': d, 'projects': {}}
    for P in EXEC_PROJS:
        if f'{P}_build_rc' not in meta:
            continue
        blog = open(os.path.join(d, f'{P}.build.log')).read()
        r['projects'][P] = {
            'build_rc': int(meta[f'{P}_build_rc']), 'build_s': float(meta.get(f'{P}_build_s', 0)),
            'errors': sorted({re.sub(WT_RE, '', e) for e in re.findall(r'[^\s]+: error \w+:[^\[]*', blog)}),
            'warnings': sorted({re.sub(r'\(\d+,\d+(,\d+,\d+)?\)', '', re.sub(WT_RE, '', w)).strip() for w in re.findall(r'[^\s]+: warning \w+:[^\[]*', blog)}),
            'cs9057': 'CS9057' in blog,
            'targeted': parse_trx(os.path.join(d, f'{P}.targeted.trx')),
            'full': parse_trx(os.path.join(d, f'{P}.full.trx')),
            'targeted_s': float(meta.get(f'{P}_targeted_s', 0)), 'full_s': float(meta.get(f'{P}_full_s', 0)),
        }
    return r


def exec_logs(label, run, change_dir, prefix, kinds=('build', 'targeted', 'full')):
    logs = []
    for P in run['projects']:
        for k in kinds:
            l = copy_log(os.path.join(run['dir'], f'{P}.{k}.log'), os.path.join(change_dir, 'logs', f'{prefix}.{P}.{k}.log'))
            if l:
                logs.append(l)
    return logs


def exec_checks(ex, change_dir, newset):
    """tests.targeted.execution, tests.execution_fail_without_fix, tests.execution_full_suite for one change."""
    head, fwf, base = exec_run(ex['label']), exec_run(ex['fwf']), exec_run(ex['base'])
    if head is None:
        return None
    out = []
    common = {'tool_version': SDK9, 'tool_version_note': SDK9_NOTE, 'filter': ex['filter'],
              'projects': [exec_proj(P) for P in head['projects']]}
    # -- head: targeted
    tests, notes = [], []
    for P, pr in head['projects'].items():
        if pr['build_rc'] != 0:
            notes.append(f'{exec_proj(P)} did not build: ' + '; '.join(pr['errors'][:5]))
            continue
        if not pr['targeted']:
            notes.append(f'{exec_proj(P)}: no tests match the filter (the test file is excluded from this project)')
        for t in pr['targeted'] or []:
            t2 = {'name': t['name'], 'project': exec_proj(P), 'outcome': t['outcome'], 'new': method_of(t['name']) in newset}
            if t['outcome'] == 'failed':
                t2['error'] = t['error']
            tests.append(t2)
    p = sum(t['outcome'] == 'passed' for t in tests)
    f = sum(t['outcome'] == 'failed' for t in tests)
    n = sum(t['new'] for t in tests)
    st = 'error' if not tests else ('pass' if f == 0 else 'fail')
    chk = {'id': 'tests.targeted.execution', 'tool': 'dotnet build + dotnet test (ExecutionTests, MapModeExecutionTests)', **common,
           'status': st, 'summary': f'{ex["class"]}: {p} passed, {f} failed ({n} new test results; runtime: generator runs inside csc, no CS9057)'
           + ('' if not notes else '; ' + '; '.join(notes)),
           'tests': tests, 'cs9057': any(pr['cs9057'] for pr in head['projects'].values()),
           'log': exec_logs(ex['label'], head, change_dir, 'execution'),
           'duration_s': sum(pr['build_s'] + pr['targeted_s'] for pr in head['projects'].values())}
    if base is not None:
        chk['on_base'] = 'tests do not exist on base (new in this change): ' + ', '.join(
            f'{exec_proj(P)} built={pr["build_rc"] == 0}, {len(pr["targeted"] or [])} matching tests' for P, pr in base['projects'].items())
    out.append(chk)
    # -- fwf: same tests with src/ reverted to base
    if fwf is not None:
        ftests, fnotes, compile_fail = [], [], []
        for P, pr in fwf['projects'].items():
            if pr['build_rc'] != 0:
                compile_fail.append({'project': exec_proj(P), 'errors': pr['errors']})
                continue
            for t in pr['targeted'] or []:
                t2 = {'name': t['name'], 'project': exec_proj(P), 'outcome': t['outcome'], 'new': method_of(t['name']) in newset}
                if t['outcome'] == 'failed':
                    t2['error'] = t['error']
                ftests.append(t2)
        head_names = {(t['project'], t['name']) for t in tests}
        fw = {'id': 'tests.execution_fail_without_fix', 'tool': 'dotnet test (source reverted, tests kept) - ExecutionTests', **common,
              'tests': ftests, 'log': exec_logs(ex['fwf'], fwf, change_dir, 'execution_fail_without_fix')}
        newt = [t for t in ftests if t['new']]
        nf = sum(t['outcome'] == 'failed' for t in newt)
        if compile_fail:
            missing = sorted({t['name'] for t in tests if t['project'] in {c['project'] for c in compile_fail}})
            fw['compile_failure'] = compile_fail
            fw['tests_not_compiled'] = missing
            fw['status'] = 'pass'
            fw['summary'] = (f'new runtime tests do not compile with the source reverted ({", ".join(c["project"] for c in compile_fail)}): '
                             f'{len(missing)} tests cannot exist without the fix; errors are the missing feature itself '
                             '(see compile_failure) -> tests depend on the change')
            fw['caveat'] = ('compile-time, not a runtime comparison: the tests cannot be built, so no serialization behaviour was compared. '
                            'Read compile_failure to see which part of the reverted source each error comes from '
                            '(e.g. CS0246 = an attribute/type from the change is missing; CS0535 = the generator emitted no members for a partial formatter).')
        elif nf > 0:
            fw['status'] = 'pass'
            fw['summary'] = f'new runtime tests fail on base source: {nf}/{len(newt)} failed -> tests do cover the change'
        else:
            fw['status'] = 'fail'
            fw['summary'] = (f'new runtime tests pass on base source: 0/{len(newt)} failed -> these runtime tests do NOT demonstrate the change '
                             '(runtime behaviour they check is identical with and without the fix)')
        fw['new_failed'] = nf
        fw['new_total'] = len(newt)
        out.append(fw)
    # -- whole projects vs base (regression)
    if base is not None:
        projs, bad = [], 0
        for P, pr in head['projects'].items():
            bp = base['projects'].get(P)
            if pr['full'] is None:
                projs.append({'project': exec_proj(P), 'status': 'error', 'reason': 'did not build/run'})
                bad += 1
                continue
            bfail = {t['name'] for t in (bp and bp['full'] or []) if t['outcome'] == 'failed'}
            failed = [t for t in pr['full'] if t['outcome'] == 'failed']
            newf = [t['name'] for t in failed if t['name'] not in bfail]
            bad += len(newf)
            bnames = {t['name'] for t in (bp and bp['full'] or [])}
            projs.append({'project': exec_proj(P), 'total': len(pr['full']), 'passed': sum(t['outcome'] == 'passed' for t in pr['full']),
                          'failed': len(failed), 'failures_not_on_base': newf,
                          'base_total': len(bp['full']) if bp and bp['full'] else None,
                          'base_passed': sum(t['outcome'] == 'passed' for t in bp['full']) if bp and bp['full'] else None,
                          'tests_added_vs_base': sorted(t['name'] for t in pr['full'] if t['name'] not in bnames),
                          'tests_missing_vs_base': sorted(bnames - {t['name'] for t in pr['full']}),
                          'new_build_warnings_vs_base': sorted(set(pr['warnings']) - set(bp['warnings'] if bp else []))})
        out.append({'id': 'tests.execution_full_suite', 'tool': 'dotnet test (whole ExecutionTests, MapModeExecutionTests) vs base', 'tool_version': SDK9,
                    'tool_version_note': SDK9_NOTE, 'status': 'pass' if bad == 0 else 'fail',
                    'summary': '; '.join(f'{x["project"]}: {x.get("passed")}/{x.get("total")} passed (base {x.get("base_passed")}/{x.get("base_total")}), '
                                         f'{len(x.get("failures_not_on_base", []))} failures not on base' for x in projs),
                    'projects': projs, 'log': exec_logs(ex['label'], head, change_dir, 'execution', kinds=('full',)),
                    'duration_s': sum(pr['full_s'] for pr in head['projects'].values())})
    return out


# ---- reviewer repros (evidence/repros/<change>/<finding>/, run by scripts/repro.py -> OUT/repro-<change>-<reviewer>-<finding>-<run>) ----

def repro_checks(n, change_dir):
    """One check `repro.<reviewer>.<finding>` per repro of change n: the reviewer's claimed defect as an executable test,
    run on each revision in repro.json. pass = every run gave the outcome the claim predicts (reproduced);
    fail = at least one did not (not reproduced); error = a run is missing, did not build, ran no test, or used another test file."""
    root = os.path.join(REPROS, n)
    out = []
    for finding in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        rp = os.path.join(root, finding, 'repro.json')
        if not os.path.exists(rp):
            continue
        spec = json.load(open(rp))
        cid = f"repro.{spec['reviewer']}.{spec['finding']}"
        digest = hashlib.sha256(open(os.path.join(root, finding, spec['test_file']), 'rb').read()).hexdigest()
        runs, problems = [], []
        for run in spec['runs']:
            lab = f"repro-{n}-{spec['reviewer']}-{spec['finding']}-{run['label']}"
            meta = read_meta(lab)
            rec = {'label': run['label'], 'rev': run['rev'], 'expect': run['expect'], 'why': run.get('why')}
            if meta is None or 'DONE' not in open(os.path.join(OUT, lab, 'meta.txt')).read():
                problems.append(f"{run['label']}: not run")
                runs.append({**rec, 'outcome': 'not_run', 'as_expected': False})
                continue
            info = json.load(open(os.path.join(OUT, lab, 'repro.json')))
            rec['sha'] = info['sha']
            if info.get('revert'):
                rec['reverted_to_base'] = info['revert']
            rec['build'] = 'pass' if meta.get('build_rc') == '0' else 'fail'
            rec['log'] = [copy_log(os.path.join(OUT, lab, 'build.log'), os.path.join(change_dir, 'logs', f'{cid}.{run["label"]}.build.log'))]
            if info['test_file_sha256'] != digest:
                problems.append(f"{run['label']}: ran a different version of {spec['test_file']} (re-run scripts/repro.py)")
            if rec['build'] == 'fail':
                problems.append(f"{run['label']}: did not build")
                runs.append({**rec, 'outcome': 'build_failed', 'as_expected': False})
                continue
            rec['log'].append(copy_log(os.path.join(OUT, lab, 'targeted.1.log'), os.path.join(change_dir, 'logs', f'{cid}.{run["label"]}.test.log')))
            trx = parse_trx(os.path.join(OUT, lab, 'targeted.1.trx')) or []
            if not trx:
                problems.append(f"{run['label']}: no test ran")
                runs.append({**rec, 'outcome': 'no_tests', 'as_expected': False})
                continue
            outcome = 'failed' if any(t['outcome'] == 'failed' for t in trx) else ('passed' if all(t['outcome'] == 'passed' for t in trx) else 'skipped')
            rec.update({'outcome': outcome, 'as_expected': outcome == run['expect'], 'duration_s': float(meta.get('build_s', 0)) + float(meta.get('targeted_1_s', 0)),
                        'tests': [{'name': t['name'], 'outcome': t['outcome'], **({'error': t['error']} if t['outcome'] == 'failed' else {})} for t in trx]})
            runs.append(rec)
        said = ', '.join(f"{r['outcome']} on {r['label']} (claim: {r['expect']})" for r in runs)
        if problems:
            status, summary = 'error', 'repro could not be judged: ' + '; '.join(problems)
        elif all(r['as_expected'] for r in runs):
            status, summary = 'pass', f"reproduced by the pipeline: {said}"
        else:
            status, summary = 'fail', f"not reproduced: {said}"
        out.append({'id': cid, 'tool': 'dotnet test (reviewer repro test copied into tests/MessagePack.SourceGenerator.Tests/CountersignRepro)',
                    'tool_version': SDK, 'status': status, 'summary': summary,
                    'reviewer': spec['reviewer'], 'finding': spec['finding'], 'kind': spec.get('kind'), 'claim': spec['claim'],
                    'supports': spec.get('supports', []), 'repro': f'evidence/repros/{n}/{finding}/',
                    'test_file': f"evidence/repros/{n}/{finding}/{spec['test_file']}", 'test_file_sha256': digest,
                    'filter': f"FullyQualifiedName~{spec['test_class']}", 'runs': runs})
    return out


# ---- injection_scan (countersign/injection.py): text planted for AI reviewers, in every change ----

def pr_text_of(facts):
    """The PR title and body, from facts['pr_text'] or facts['pr_title'] / facts['pr_body'] or facts['pr'] {title, body}."""
    if facts.get('pr_text'):
        return facts['pr_text']
    pr = facts.get('pr') if isinstance(facts.get('pr'), dict) else {}
    parts = [facts.get('pr_title') or pr.get('title') or '', facts.get('pr_body') or pr.get('body') or '']
    return '\n'.join(x for x in parts if x)


def injection_check(facts):
    """Scan what the change adds: `git diff base head` (added lines, every file type, the paths of added/changed files,
    binary files reported as unscannable), the seeded edit of a mutant (mutation.file/line/after), the branch name, the
    commit message and the PR title/body (facts['pr_text'] or pr_title/pr_body, if any)."""
    from countersign import injection
    base, head = facts.get('base_full') or BASE, facts.get('head_full') or facts['head']
    diff = subprocess.run(['git', '-C', REPO, 'diff', '--no-color', '--no-ext-diff', base, head], capture_output=True, check=True).stdout.decode('utf-8', 'replace')
    mut = facts.get('mutation') or {}
    added = [(mut['file'], int(mut['line']), mut['after'])] if mut.get('file') and mut.get('after') else []
    by_file = (facts.get('diff') or {}).get('by_file') or []
    pr_text = pr_text_of(facts)
    src = {'diff': f'git diff {base[:8]} {head[:8]} (added lines and file paths)' + (' + the seeded edit (mutation.after)' if added else ''),
           'branch': 'facts.branch' if facts.get('branch') else 'none',
           'commit_message': 'facts.commit_message', 'pr_text': 'facts PR title/body' if pr_text else 'none: the change has no pull request text'}
    return injection.scan(diff=diff, commit_message=facts.get('commit_message') or '', pr_text=pr_text, added=added, sources=src,
                          branch=facts.get('branch') or '', paths=[f['path'] for f in by_file],
                          binary=[f['path'] for f in by_file if f.get('kind') == 'binary'])


def update_injection(ids):
    """--injection-only: add or replace the injection_scan check in existing evidence/<id>/facts.json files, leaving
    every other byte as it was (for facts written by other generators, e.g. measurement/mutants/seed.py)."""
    for n in ids:
        p = os.path.join(EVID, n, 'facts.json')
        raw = open(p, encoding='utf-8').read()
        facts = json.loads(raw)
        nl = raw.endswith('\n')
        if json.dumps(facts, indent=2) + ('\n' if nl else '') != raw:
            print(n, 'SKIPPED: facts.json is not in json.dumps(indent=2) form, so it cannot be rewritten byte-for-byte')
            continue
        chk = injection_check(facts)
        cs = facts['checks']
        i = next((k for k, c in enumerate(cs) if c['id'] == 'injection_scan'), None)
        if i is None:
            cs.append(chk)
        else:
            cs[i] = chk
        open(p, 'w', encoding='utf-8').write(json.dumps(facts, indent=2) + ('\n' if nl else ''))
        print(n, chk['status'], chk['summary'])


# ---- tests.fail_without_fix for seeded variants: inherited from the unmutated original ----

FWF_INHERIT_NOTE = ('inherited, not re-run: fail-without-fix reverts src/ to base and keeps the branch tests. A seeded variant '
                    '(one-line mutant or planted injection text) changes only its own edit, which the revert removes, so the '
                    'tree under test is byte-identical to the original\'s and the result is the same computation. It says '
                    'whether the tests demonstrate the original change; it says nothing about the seeded edit.')


def inherited_fwf(change):
    """The original's tests.fail_without_fix check for a seeded variant <orig>-mutK / <orig>-inject, marked
    inherited_from, or None if the original has none."""
    orig = re.sub(r'-(mut\d+|inject\d*|sec\d+)$', '', change)
    if orig == change:
        return None
    p = os.path.join(EVID, orig, 'facts.json')
    if not os.path.exists(p):
        return None
    c = next((c for c in json.load(open(p, encoding='utf-8')).get('checks', []) if c['id'] == 'tests.fail_without_fix'), None)
    return c and {**c, 'inherited_from': orig, 'note': FWF_INHERIT_NOTE}


def put_inherited_fwf(facts):
    """Insert the inherited tests.fail_without_fix after tests.targeted (the original's order) and drop it from not_run."""
    c = inherited_fwf(facts['change'])
    if c is None:
        return None
    cs = [x for x in facts['checks'] if x['id'] != 'tests.fail_without_fix']
    i = next((k + 1 for k, x in enumerate(cs) if x['id'] == 'tests.targeted'), len(cs))
    facts['checks'] = cs[:i] + [c] + cs[i:]
    facts['not_run'] = [x for x in facts.get('not_run', []) if x['id'] != 'tests.fail_without_fix']
    return c


def update_inherited_fwf(ids):
    """--inherit-fwf: add the original's tests.fail_without_fix to existing seeded-variant facts.json files, leaving
    every other check byte-identical."""
    for n in ids:
        p = os.path.join(EVID, n, 'facts.json')
        raw = open(p, encoding='utf-8').read()
        facts = json.loads(raw)
        nl = raw.endswith('\n')
        if json.dumps(facts, indent=2) + ('\n' if nl else '') != raw:
            print(n, 'SKIPPED: facts.json is not in json.dumps(indent=2) form, so it cannot be rewritten byte-for-byte')
            continue
        c = put_inherited_fwf(facts)
        if c is None:
            print(n, 'SKIPPED: the original has no tests.fail_without_fix')
            continue
        open(p, 'w', encoding='utf-8').write(json.dumps(facts, indent=2) + ('\n' if nl else ''))
        print(n, 'tests.fail_without_fix', c['status'], 'inherited from', c['inherited_from'])


def main():
    os.makedirs(EVID, exist_ok=True)
    base_meta = read_meta('base')
    base_full = parse_trx(os.path.join(OUT, 'base', 'full.trx')) or []
    base_fail = {t['name'] for t in base_full if t['outcome'] == 'failed'}
    base_warn = warnings('base')
    spec = json.load(open(SPEC))
    # base summary (for reference)
    bd = os.path.join(EVID, 'base')
    copy_log(os.path.join(OUT, 'base', 'build.log'), os.path.join(bd, 'logs', 'build.log'))
    copy_log(os.path.join(OUT, 'base', 'full.log'), os.path.join(bd, 'logs', 'tests_full_suite.log'))
    copy_log(os.path.join(OUT, 'exec-base', 'build.log'), os.path.join(bd, 'logs', 'execution_tests.build.log'))
    bx = exec_run('base')
    if bx is not None:
        exec_logs('base', bx, bd, 'execution_sdk9')
    json.dump({'label': 'base', 'sha': BASE, 'build_rc': base_meta.get('build_rc'),
               'full_suite': {'total': len(base_full), 'passed': sum(t['outcome'] == 'passed' for t in base_full), 'failed': sorted(base_fail)},
               'warnings': sorted(base_warn), 'tests': base_full and [{'name': t['name'], 'outcome': t['outcome']} for t in base_full]},
              open(os.path.join(bd, 'base_results.json'), 'w'), indent=1)

    for ch in spec['changes']:
        n = ch['change']
        if ONLY and n != ONLY:
            continue
        branch = f'ju26-issue-{n.split("-")[0]}'
        head = git('rev-parse', f'origin/{branch}').strip()
        cd = os.path.join(EVID, n)
        if os.path.isdir(os.path.join(cd, 'logs')):
            shutil.rmtree(os.path.join(cd, 'logs'))
        os.makedirs(cd, exist_ok=True)
        msg = git('log', '-1', '--format=%B', head).strip()
        author = git('log', '-1', '--format=%an', head).strip()
        newset = new_tests(head)
        facts = {'change': n, 'branch': branch, 'base': BASE[:8], 'head': head[:8], 'base_full': BASE, 'head_full': head,
                 'commit_message': msg, 'author': author, 'agent_written': True,
                 'diff': diff_facts(head), 'new_tests_in_diff': sorted(newset)}
        if 'mutation' in ch:
            facts['mutation'] = ch['mutation']
            facts['diff_note'] = 'diff/commit fields describe the unmutated branch; the mutation is applied on top of head as an uncommitted edit'
        meta = read_meta(ch['label'])
        checks = []
        b, wl = build_check(ch['label'], cd, meta)
        checks.append(b)
        if meta.get('build_rc') == '0':
            t = targeted_check(ch['label'], cd, meta, newset)
            t['filter'] = ch['filters']
            t['project'] = SG
            checks.append(t)
        if 'mutation' in ch:
            failed = [x['name'] for x in t['tests'] if x['outcome'] == 'failed']
            facts['mutation']['caught'] = bool(failed)
            facts['mutation']['caught_by'] = failed
            facts['mutation']['targeted_summary'] = t['summary']
            fc = full_check(ch['label'], cd, meta, base_fail)
            if fc:
                checks.append(fc)
                facts['mutation']['caught_by_full_suite'] = [x['name'] for x in fc['failures_not_on_base']]
            facts['mutation']['caught_by_any_deterministic_check'] = bool(failed) or bool(fc and fc['failures_not_on_base'])
        if ch.get('fwf'):
            fm = read_meta(ch['fwf'])
            if fm is None:
                checks.append({'id': 'tests.fail_without_fix', 'status': 'skipped', 'summary': 'not run'})
            elif fm.get('build_rc') != '0':
                copy_log(os.path.join(OUT, ch['fwf'], 'build.log'), os.path.join(cd, 'logs', 'fail_without_fix.build.log'))
                checks.append({'id': 'tests.fail_without_fix', 'tool': 'dotnet test (source reverted, tests kept)', 'status': 'error',
                               'summary': 'build failed with source reverted to base (tests do not compile against base source)',
                               'log': f'evidence/{n}/logs/fail_without_fix.build.log'})
            else:
                fw = targeted_check(ch['fwf'], cd, fm, newset, id_='tests.fail_without_fix', tool='dotnet test (source reverted, tests kept)')
                newt = [x for x in fw['tests'] if x['new']]
                nf = sum(x['outcome'] == 'failed' for x in newt)
                oldf = sum(x['outcome'] == 'failed' for x in fw['tests'] if not x['new'])
                fw['reverted_files'] = ch['reverted']
                ff = parse_trx(os.path.join(OUT, ch['fwf'], 'full.trx'))
                if ff is not None:
                    copy_log(os.path.join(OUT, ch['fwf'], 'full.log'), os.path.join(cd, 'logs', 'fail_without_fix.full_suite.log'))
                    fl = [x['name'] for x in ff if x['outcome'] == 'failed']
                    fw['full_suite_with_source_reverted'] = {'total': len(ff), 'failed': len(fl), 'failed_tests': fl,
                                                             'log': f'evidence/{n}/logs/fail_without_fix.full_suite.log'}
                fw['new_failed'] = nf
                fw['new_total'] = len(newt)
                if nf > 0:
                    fw['status'] = 'pass'
                    fw['summary'] = f'new tests fail on base source: {nf}/{len(newt)} failed -> tests do cover the change' + (f' ({len(newt) - nf} new tests pass without the fix)' if nf < len(newt) else '') + (f'; {oldf} pre-existing tests also failed' if oldf else '')
                else:
                    fw['status'] = 'fail'
                    fw['summary'] = f'new tests pass on base source: 0/{len(newt)} failed -> tests do NOT demonstrate the change'
                checks.append(fw)
        elif not ch.get('mutation'):
            checks.append({'id': 'tests.fail_without_fix', 'status': 'skipped', 'summary': ch.get('fwf_skip_reason', 'not run'), 'reason': ch.get('fwf_skip_reason', 'not run')})
        if not ch.get('mutation'):
            fc = full_check(ch['label'], cd, meta, base_fail)
            if fc:
                checks.append(fc)
            else:
                checks.append({'id': 'tests.full_suite', 'status': 'skipped', 'summary': 'not run', 'reason': 'not run'})
            checks.append(ch['public_api'])
            newwarn = sorted(set(wl) - base_warn)
            gone = sorted(base_warn - set(wl))
            checks.append({'id': 'analyzers', 'tool': 'dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base', 'status': 'pass' if not newwarn else 'fail',
                           'summary': 'no new warnings' if not newwarn else f'{len(newwarn)} new warnings vs base',
                           'new_warnings': newwarn, 'resolved_warnings': gone, 'base_warning_count': len(base_warn)})
        if os.path.exists(os.path.join(OUT, 'exec-' + n, 'build.log')):
            # SDK 8.0.402 attempt (CS9057), kept for the record
            copy_log(os.path.join(OUT, 'exec-' + n, 'build.log'), os.path.join(cd, 'logs', 'execution_tests.sdk8.build.log'))
        extra = [dict(c) for c in ch.get('extra_checks', [])]
        for c in extra:
            if c['id'] == 'tests.targeted.execution' and 'log' in c:
                c['log'] = f'evidence/{n}/logs/execution_tests.sdk8.build.log'
        if 'execution' in ch:
            ec = exec_checks(ch['execution'], cd, newset)
            if ec:
                ec[0]['sdk8_attempt'] = {'tool_version': SDK, 'status': 'error', 'reason': 'CS9057: generator references Microsoft.CodeAnalysis 4.12, SDK 8.0.402 ships Roslyn 4.11',
                                         'log': f'evidence/{n}/logs/execution_tests.sdk8.build.log'}
                extra = [c for c in extra if c['id'] != 'tests.targeted.execution']
                checks.extend(ec)
        checks.extend(extra)
        checks.extend(repro_checks(n, cd))
        facts['checks'] = checks
        checks.append(injection_check(facts))
        facts['not_run'] = ch.get('not_run', [])
        if 'mutation' in ch:
            put_inherited_fwf(facts)
        facts['environment'] = {'sdk': SDK, **({'sdk_execution_tests': SDK9, 'sdk_note': SDK9_NOTE} if 'execution' in ch else {}), 'os': OS_DESC, 'configuration': 'Debug', 'max_cpu': 8}
        json.dump(facts, open(os.path.join(cd, 'facts.json'), 'w'), indent=2)
        print(n, [(c['id'], c['status']) for c in checks])


if __name__ == '__main__':
    if '--injection-only' in sys.argv:
        update_injection(sys.argv[sys.argv.index('--injection-only') + 1:])
    elif '--inherit-fwf' in sys.argv:
        update_inherited_fwf(sys.argv[sys.argv.index('--inherit-fwf') + 1:])
    else:
        main()
