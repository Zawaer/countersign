#!/usr/bin/env python3
"""Assemble Countersign stage-1 facts.json files from the raw run outputs in /data/work/out."""
import json, os, re, shutil, subprocess, xml.etree.ElementTree as ET

REPO = '/data/src/mp'
OUT = '/data/work/out'
EVID = '/data/worktrees/s_Vga5T2JJtb/evidence'
BASE = '32258fdbee4bcd653c79f51b4376b5103c6f4d27'
SDK = '8.0.402'
SG = 'tests/MessagePack.SourceGenerator.Tests'
NS = '{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}'
MAXLOG = 200_000


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True, check=True).stdout


def kind(path):
    p = path
    if p.endswith('.g.cs'):
        return 'generated'
    if p.endswith(('.md', '.txt')) and 'PublicAPI' not in p or p.startswith('doc/'):
        return 'build' if p.endswith('AnalyzerReleases.Unshipped.md') or p.endswith('AnalyzerReleases.Shipped.md') else 'doc'
    if p.endswith(('.csproj', '.props', '.targets', '.sln', '.json', '.yml', '.yaml')) or 'PublicAPI' in p:
        return 'build'
    if p.startswith('tests/'):
        return 'test'
    if p.endswith('.cs') and os.path.exists(os.path.join(REPO, p[:-3] + '.tt')) or (p.endswith('.cs') and git_has_tt(p)):
        return 'generated'
    return 'source'


_tt_cache = {}


def git_has_tt(p):
    # T4-generated .cs next to a .tt template (checked on the change head via ls-tree in the caller's rev)
    return _tt_cache.get(p[:-3] + '.tt', False)


def diff_facts(head):
    files = git('diff', '--name-only', BASE, head).split()
    for f in git('ls-tree', '-r', '--name-only', head).split():
        if f.endswith('.tt'):
            _tt_cache[f] = True
    by = []
    ins = dele = 0
    for line in git('diff', '--numstat', BASE, head).splitlines():
        a, d, p = line.split('\t')
        a, d = int(a), int(d)
        ins += a; dele += d
        by.append({'path': p, 'ins': a, 'del': d, 'kind': kind(p)})
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
                l = re.sub(r'/data/src/mp-[\w-]+/', '', l)
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


def main():
    os.makedirs(EVID, exist_ok=True)
    base_meta = read_meta('base')
    base_full = parse_trx(os.path.join(OUT, 'base', 'full.trx')) or []
    base_fail = {t['name'] for t in base_full if t['outcome'] == 'failed'}
    base_warn = warnings('base')
    spec = json.load(open('/data/work/scripts/spec.json'))
    # base summary (for reference)
    bd = os.path.join(EVID, 'base')
    copy_log(os.path.join(OUT, 'base', 'build.log'), os.path.join(bd, 'logs', 'build.log'))
    copy_log(os.path.join(OUT, 'base', 'full.log'), os.path.join(bd, 'logs', 'tests_full_suite.log'))
    for k in ('base', '2234', '2129'):
        copy_log(os.path.join(OUT, 'exec-' + k, 'build.log'), os.path.join(EVID, k, 'logs', 'execution_tests.build.log'))
    json.dump({'label': 'base', 'sha': BASE, 'build_rc': base_meta.get('build_rc'),
               'full_suite': {'total': len(base_full), 'passed': sum(t['outcome'] == 'passed' for t in base_full), 'failed': sorted(base_fail)},
               'warnings': sorted(base_warn), 'tests': base_full and [{'name': t['name'], 'outcome': t['outcome']} for t in base_full]},
              open(os.path.join(bd, 'base_results.json'), 'w'), indent=1)

    for ch in spec['changes']:
        n = ch['change']
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
        checks.extend(ch.get('extra_checks', []))
        facts['checks'] = checks
        facts['not_run'] = ch.get('not_run', [])
        facts['environment'] = {'sdk': SDK, 'os': 'linux-x64 (container)', 'configuration': 'Debug', 'max_cpu': 8}
        json.dump(facts, open(os.path.join(cd, 'facts.json'), 'w'), indent=2)
        print(n, [(c['id'], c['status']) for c in checks])


if __name__ == '__main__':
    main()
