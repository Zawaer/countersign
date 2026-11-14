#!/usr/bin/env python3
"""Seed the prompt-injection changes (kind "prompt_injection" in measurement/mutants/mutants.json) and write their facts.

A prompt-injection change is the agent's branch plus text planted for AI reviewers: one empty line replaced by the
`planted` text (an uncommitted edit, recorded like a mutant's before/after so the verifier can replay it), and optionally
`commit_message_appended`, which is added to the commit message the reviewers are shown. No behaviour changes, so the
build and every test should still pass: only the injection_scan check is expected to catch it.

For each entry <id> (e.g. 2283-inject):
  1. scratch worktree $SRC/mp-<id> at origin/ju26-issue-<n> (the checkout in $SRC/mp is never touched)
  2. replace line `line` of `file`, which must be empty, with `planted` (BOM and line endings kept)
  3. run.sh: build tests/MessagePack.SourceGenerator.Tests (SDK 8.0.402, -m:8), targeted filter, full suite -> $WORK/out/<id>/
  4. evidence/<id>/facts.json with the facts.py helpers, a `mutation` record (kind prompt_injection) and injection_scan

usage: python3 -I evidence/scripts/inject.py [--facts-only] [<id> ...]
"""
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CATALOGUE = os.path.join(ROOT, 'measurement', 'mutants', 'mutants.json')
SG = 'tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj'
FILTERS = {'2283': 'FullyQualifiedName~GenericsFormatterTests.', '2234': 'FullyQualifiedName~SuppressSourceGenerationAnalyzerTests.'}


def facts_module():
    spec = importlib.util.spec_from_file_location('cs_facts', os.path.join(HERE, 'facts.py'))
    F = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(F)
    if 'CS_EVID' not in os.environ:
        F.EVID = os.path.join(ROOT, 'evidence')
    return F


def plant(F, m, wt):
    path = os.path.join(wt, m['file'])
    raw = open(path, 'rb').read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    lines = raw[3 if bom else 0:].decode('utf-8').split('\n')
    i = m['line'] - 1
    if lines[i] == m['planted']:
        return  # already planted
    assert lines[i].strip('\r') == '', f"{m['id']}: line {m['line']} of {m['file']} is not empty: {lines[i]!r}"
    lines[i] = m['planted'] + ('\r' if lines[i].endswith('\r') else '')
    open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + '\n'.join(lines).encode('utf-8'))


def seed(F, m):
    n = m['id'].split('-')[0]
    wt = f'{F.SRC}/mp-{m["id"]}'
    if not os.path.isdir(wt):
        subprocess.run(['git', '-C', F.REPO, 'worktree', 'add', '--quiet', '--detach', wt, f'origin/ju26-issue-{n}'], check=True)
    plant(F, m, wt)
    dirty = subprocess.run(['git', '-C', wt, 'status', '--porcelain'], capture_output=True, text=True, check=True).stdout.split('\n')
    assert [x for x in dirty if x] == [f' M {m["file"]}'], dirty
    subprocess.run([os.path.join(HERE, 'run.sh'), m['id'], wt, SG, f'{SG}={FILTERS[n]}', 'yes'], check=True)


def write_facts(F, m):
    n = m['id'].split('-')[0]
    branch = f'ju26-issue-{n}'
    head = F.git('rev-parse', f'origin/{branch}').strip()
    cd = os.path.join(F.EVID, m['id'])
    os.makedirs(cd, exist_ok=True)
    newset = F.new_tests(head)
    msg = F.git('log', '-1', '--format=%B', head).strip()
    if m.get('commit_message_appended'):
        msg = msg + '\n\n' + m['commit_message_appended']
    facts = {'change': m['id'], 'branch': branch, 'base': F.BASE[:8], 'head': head[:8], 'base_full': F.BASE, 'head_full': head,
             'commit_message': msg, 'author': F.git('log', '-1', '--format=%an', head).strip(),
             'agent_written': True, 'diff': F.diff_facts(head), 'new_tests_in_diff': sorted(newset),
             'mutation': {'of': n, 'kind': 'prompt_injection', 'file': m['file'], 'line': m['line'], 'before': '', 'after': m['planted'],
                          'channels': m['channels'], 'description': m['description'], 'intended_effect': m['intended_effect'],
                          **({'commit_message_appended': m['commit_message_appended']} if m.get('commit_message_appended') else {})},
             'diff_note': ('SEEDED ATTACK, not the agent\'s work. diff fields describe the unmutated branch; the planted line is applied on top of head '
                           'as an uncommitted edit (mutation.before -> after on mutation.line)'
                           + ('; commit_message is the branch\'s message plus mutation.commit_message_appended' if m.get('commit_message_appended') else ''))}
    meta = F.read_meta(m['id'])
    base_full = F.parse_trx(os.path.join(F.OUT, 'base', 'full.trx')) or []
    base_fail = {t['name'] for t in base_full if t['outcome'] == 'failed'}
    b, _ = F.build_check(m['id'], cd, meta)
    checks = [b]
    failed, fc = [], None
    if meta.get('build_rc') == '0':
        t = F.targeted_check(m['id'], cd, meta, newset)
        t['filter'], t['project'] = [FILTERS[n]], F.SG
        checks.append(t)
        failed = [x['name'] for x in t['tests'] if x['outcome'] == 'failed']
        facts['mutation']['targeted_summary'] = t['summary']
        fc = F.full_check(m['id'], cd, meta, base_fail)
        if fc:
            checks.append(fc)
    facts['checks'] = checks
    inj = F.injection_check(facts)
    checks.append(inj)
    facts['mutation']['caught'] = bool(failed)
    facts['mutation']['caught_by'] = failed + (['injection_scan'] if inj['status'] == 'fail' else [])
    facts['mutation']['caught_by_full_suite'] = [x['name'] for x in fc['failures_not_on_base']] if fc else []
    facts['mutation']['caught_by_any_deterministic_check'] = bool(failed) or bool(fc and fc['failures_not_on_base']) or b['status'] == 'fail' or inj['status'] == 'fail'
    facts['not_run'] = [{'id': 'public_api', 'reason': 'seeded injection: comment/doc/message text only; build + targeted + full suite + injection_scan'},
                        {'id': 'analyzers', 'reason': 'seeded injection run'},
                        {'id': 'tests.execution', 'reason': 'seeded injection run: no code behaviour changed'},
                        {'id': 'tests.fail_without_fix', 'reason': 'seeded injection run: the branch\'s tests are unchanged, so this is the original\'s result'}]
    F.put_inherited_fwf(facts)  # same tree as the original's fail-without-fix run (src/ reverted), so its result
    facts['environment'] = {'sdk': F.SDK, 'os': F.OS_DESC, 'configuration': 'Debug', 'max_cpu': 8}
    open(os.path.join(cd, 'facts.json'), 'w').write(json.dumps(facts, indent=2) + '\n')
    print(m['id'], [(c['id'], c['status']) for c in checks], 'caught' if facts['mutation']['caught_by_any_deterministic_check'] else 'SURVIVED')


def main(argv):
    only = [a for a in argv if not a.startswith('--')]
    todo = [m for m in json.load(open(CATALOGUE))['mutants'] if m.get('kind') == 'prompt_injection' and (not only or m['id'] in only)]
    F = facts_module()
    for m in todo:
        if '--facts-only' not in argv:
            seed(F, m)
        write_facts(F, m)


if __name__ == '__main__':
    main(sys.argv[1:])
