#!/usr/bin/env python3
"""Run reviewer repro tests (evidence/repros/<change>/<finding>/) on head and base in scratch worktrees.

A repro is a reviewer's claimed defect written down as an xunit test in tests/MessagePack.SourceGenerator.Tests style,
plus repro.json saying which revisions to run it on and the outcome the claim predicts on each (e.g. a regression:
fails on head, passes on base). For every run this script
  1. makes (or resets) the scratch worktree $SRC/mp-repro-<change>-<finding>-<label> at the run's revision
     (head = origin/ju26-issue-<n>, base = BASE; optional "revert": [paths] puts those files back to base on top of head),
  2. copies the test file into tests/MessagePack.SourceGenerator.Tests/CountersignRepro/ (the only edit),
  3. builds and runs it with run.sh (SDK 8.0.402, -m:8, filter FullyQualifiedName~<test_class>) -> $WORK/out/<label>/,
  4. writes $WORK/out/<label>/repro.json: what was run (revision sha, sha256 of the copied test file).
facts.py turns those runs into the check `repro.<reviewer>.<finding>` (see repro_checks there).
The checkout in $SRC/mp is never touched; only worktrees are added next to it.

usage: python3 -I evidence/scripts/repro.py [<change>/<finding> ...]     (default: every repro under evidence/repros)
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPROS = os.environ.get('CS_REPROS', os.path.join(HERE, '..', 'repros'))
SRC = os.environ.get('CS_SRC', '/data/src')
REPO = os.environ.get('CS_REPO', SRC + '/mp')
WORK = os.environ.get('WORK', '/data/work')
BASE = '32258fdbee4bcd653c79f51b4376b5103c6f4d27'
SG = 'tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj'
DEST = 'tests/MessagePack.SourceGenerator.Tests/CountersignRepro'


def git(*a, cwd=REPO):
    return subprocess.run(['git', '-C', cwd, *a], capture_output=True, text=True, check=True).stdout.strip()


def label(spec, run):
    return f"repro-{spec['change']}-{spec['reviewer']}-{spec['finding']}-{run['label']}"


def all_repros():
    out = []
    for change in sorted(os.listdir(REPROS)) if os.path.isdir(REPROS) else []:
        for finding in sorted(os.listdir(os.path.join(REPROS, change))):
            if os.path.exists(os.path.join(REPROS, change, finding, 'repro.json')):
                out.append(f'{change}/{finding}')
    return out


def rev_sha(change, rev):
    if rev == 'base':
        return BASE
    if rev == 'head':
        return git('rev-parse', f"origin/ju26-issue-{change.split('-')[0]}")
    return git('rev-parse', rev)


def run_one(path):
    d = os.path.join(REPROS, path)
    spec = json.load(open(os.path.join(d, 'repro.json')))
    test = os.path.join(d, spec['test_file'])
    digest = hashlib.sha256(open(test, 'rb').read()).hexdigest()
    for run in spec['runs']:
        sha = rev_sha(spec['change'], run['rev'])
        wt = f"{SRC}/mp-repro-{spec['change']}-{spec['finding']}-{run['label']}"
        if not os.path.isdir(wt):
            git('worktree', 'add', '--quiet', '--detach', wt, sha)
        else:  # reset a reused scratch worktree to exactly the revision
            git('checkout', '--quiet', '--force', '--detach', sha, cwd=wt)
            git('clean', '-fdq', '--', 'tests', 'src', cwd=wt)
        for p in run.get('revert', []):
            git('checkout', '--quiet', BASE, '--', p, cwd=wt)
        os.makedirs(os.path.join(wt, DEST), exist_ok=True)
        shutil.copyfile(test, os.path.join(wt, DEST, spec['test_file']))
        lab = label(spec, run)
        out = os.path.join(WORK, 'out', lab)
        shutil.rmtree(out, ignore_errors=True)
        print(f'{lab}: {run["rev"]} {sha[:8]} in {wt}', flush=True)
        subprocess.run([os.path.join(HERE, 'run.sh'), lab, wt, SG, f'{SG}=FullyQualifiedName~{spec["test_class"]}', 'no'], check=True)
        json.dump({'repro': f'evidence/repros/{path}', 'rev': run['rev'], 'sha': sha, 'revert': run.get('revert', []),
                   'test_file': f'{DEST}/{spec["test_file"]}', 'test_file_sha256': digest,
                   'dirty': git('status', '--porcelain', cwd=wt).splitlines()},
                  open(os.path.join(out, 'repro.json'), 'w'), indent=1)


def main(argv):
    for path in argv or all_repros():
        run_one(path)
    print('ALLDONE')


if __name__ == '__main__':
    main(sys.argv[1:])
