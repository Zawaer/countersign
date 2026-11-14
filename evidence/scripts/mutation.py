#!/usr/bin/env python3
"""tests.mutation: do the change's new tests kill small mutants of the change's own source lines?

fail-without-fix shows that a new test fails when the whole fix is reverted. It does not show that the test checks
what the fix does: a test that fails on base only because it looks for a method the fix renamed (red team TT1) passes
that check. Mutation testing asks the narrower question per changed line: if this line were subtly wrong, would a new
test notice?

1. Mutants (deterministic, at most MAX_MUTANTS per change). The changed *source* lines are the lines `git diff -U0
   BASE head` adds in files stage 1 classifies `source` (facts.py kind(): not tests, docs, build files or generated
   output), C# only. Comment and XML-doc lines, blank lines and lone braces are skipped. Each diff hunk is split at
   blank lines into units ("hunks" in the check). Operators, tried in this order on each line of a unit:
     negate_condition     if (c) -> if (!(c));  `x is null ?` -> `x is not null ?`
     drop_statement       continue; / return; / break;  -> { }
     drop_guard           if (c) -> if (true)
     swap_logical         the first top-level && <-> ||
     drop_guard_conjunct  if (a && b) -> if (a)   (the last conjunct of a guard removed)
     return_default       return x; -> return default;  member => x; -> member => default;
     remove_call          a call statement `x.M(...);` -> { }
   Selection is round-robin over the units in diff order (the first candidate of every unit, then the second, ...),
   so every unit that has a candidate gets a mutant before any unit gets a second one; with more such units than
   the budget, the units are spread evenly over the change (select()).
2. Run. Each mutant is applied alone to a scratch worktree of the branch head ($SRC/mp-<n>-mt, reset between
   mutants; /data/src/mp itself is never touched), built and run with run.sh using the change's targeted filter (the
   filter tests.fail_without_fix uses) -> $WORK/out/<n>-mt<k>/ (+ mutant.json, mutant.diff).
3. Judge. A mutant is `killed` when at least one new test (new: true in the change's tests.fail_without_fix) fails
   on it; `survived` when every new test passes; `not_viable` when it does not build. A unit is killed when one of
   its mutants is. Status: pass = every mutated unit has a killed mutant; fail = some mutated unit has only
   surviving mutants (listed); error = no mutant could be judged. Units with no applicable operator, or left out by
   the budget, are listed as not mutated and do not decide the status.

usage: python3 -I evidence/scripts/mutation.py plan <n>...    print the mutants
       python3 -I evidence/scripts/mutation.py run <n>...     run them (needs the .NET SDK, see evidence/README.md)
       python3 -I evidence/scripts/mutation.py facts <n>...   append tests.mutation to evidence/<n>/facts.json
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import facts as F  # noqa: E402  (stage 1's own kind(), parse_trx(), copy_log(); paths from the same env vars)

WORK = os.environ.get('WORK', '/data/work')
MAX_MUTANTS = 8
CHECK_ID = 'tests.mutation'
SG_PROJ = F.SG + '/MessagePack.SourceGenerator.Tests.csproj'
OPERATORS = ['negate_condition', 'drop_statement', 'drop_guard', 'swap_logical', 'drop_guard_conjunct', 'return_default', 'remove_call']
KEYWORDS = {'if', 'while', 'for', 'foreach', 'return', 'throw', 'new', 'var', 'using', 'lock', 'switch', 'nameof', 'typeof',
            'await', 'yield', 'else', 'case', 'default', 'base', 'checked', 'unchecked', 'fixed'}


def git(*a, cwd=None):
    return subprocess.run(['git', '-C', cwd or F.REPO, *a], capture_output=True, text=True, check=True).stdout


def spec_of(n):
    return next(c for c in json.load(open(F.SPEC))['changes'] if c['change'] == n)


def head_of(n):
    return git('rev-parse', f'origin/ju26-issue-{n}').strip()


# ---- code lines -------------------------------------------------------------------------------------------------

def code_part(line):
    """The line without a trailing // comment (outside string literals) and without the line ending."""
    s = line.rstrip('\r\n')
    q = None
    i = 0
    while i < len(s):
        ch = s[i]
        if q:
            if ch == '\\':
                i += 2
                continue
            if ch == q:
                q = None
        elif ch in '"\'':
            q = ch
        elif s.startswith('//', i):
            return s[:i].rstrip()
        i += 1
    return s.rstrip()


def is_code(line):
    s = line.strip()
    return bool(s) and not s.startswith(('//', '/*', '*', '#')) and s not in ('{', '}', '};', ');', '},')


def matching_paren(s, i):
    """Index of the ) closing the ( at s[i], or -1 (strings skipped)."""
    depth, q, j = 0, None, i
    while j < len(s):
        ch = s[j]
        if q:
            if ch == '\\':
                j += 2
                continue
            if ch == q:
                q = None
        elif ch in '"\'':
            q = ch
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return -1


def top_level(s, op):
    """Positions of `op` in s outside parentheses and strings."""
    out, depth, q, j = [], 0, None, 0
    while j < len(s):
        ch = s[j]
        if q:
            if ch == '\\':
                j += 2
                continue
            if ch == q:
                q = None
        elif ch in '"\'':
            q = ch
        elif ch in '([{':
            depth += 1
        elif ch in ')]}':
            depth -= 1
        elif depth == 0 and s.startswith(op, j):
            out.append(j)
            j += len(op)
            continue
        j += 1
    return out


def balanced(s):
    return matching_paren('(' + s + ')', 0) == len(s) + 1


def candidates(line):
    """[(operator, mutated line)] for one source line, in OPERATORS order. The line ending and any comment stay."""
    eol = line[len(line.rstrip('\r\n')):]
    raw = line.rstrip('\r\n')
    code = code_part(raw)
    tail = raw[len(code):]
    indent = raw[:len(raw) - len(raw.lstrip())]
    stmt = code.strip()
    out = []

    def put(op, new_code):
        if new_code != code:
            out.append((op, new_code + tail + eol))

    m = re.match(r'(\s*(?:else\s+)?(?:if|while)\s*)\(', code)
    cond = None
    if m:
        i = m.end() - 1
        j = matching_paren(code, i)
        if j > 0 and code[j + 1:].strip() in ('', '{'):
            cond = (i, j, code[i + 1:j])
    tern = re.search(r'\bis null \?', code)
    # negate_condition
    if cond:
        i, j, c = cond
        put('negate_condition', code[:i + 1] + f'!({c})' + code[j:])
    elif tern:
        put('negate_condition', code[:tern.start()] + 'is not null ?' + code[tern.end():])
    # drop_statement
    if re.fullmatch(r'(continue|break|return)\s*;', stmt):
        put('drop_statement', indent + '{ }')
    # drop_guard
    if cond and cond[2].strip() != 'true':
        i, j, c = cond
        put('drop_guard', code[:i + 1] + 'true' + code[j:])
    # swap_logical
    target = cond[2] if cond else code
    hits = sorted([(p, '&&') for p in top_level(target, '&&')] + [(p, '||') for p in top_level(target, '||')])
    if hits:
        p, op = hits[0]
        new_t = target[:p] + ('||' if op == '&&' else '&&') + target[p + 2:]
        put('swap_logical', code[:cond[0] + 1] + new_t + code[cond[1]:] if cond else new_t)
    # drop_guard_conjunct
    if cond:
        i, j, c = cond
        ands = top_level(c, '&&')
        if ands and not top_level(c, '||'):
            put('drop_guard_conjunct', code[:i + 1] + c[:ands[-1]].rstrip() + code[j:])
    # return_default
    r = re.fullmatch(r'(\s*return\s+)(.+);', code)
    if r and r.group(2).strip() not in ('default', 'null', 'false', 'true', '0'):
        put('return_default', r.group(1) + 'default;')
    e = re.fullmatch(r'(\s*(?:(?:public|private|internal|protected|static|override|virtual|sealed|async|readonly|new|unsafe|extern)\s+)+'
                     r'[^=;{}]*?=>\s*)(.+);', code)
    if e and e.group(2).strip() not in ('default', 'null'):
        put('return_default', e.group(1) + 'default;')
    # remove_call
    c = re.fullmatch(r'((?:this\.)?[A-Za-z_]\w*(?:(?:\?\.|\.)[A-Za-z_]\w*)*(?:<[^()]*>)?)\((.*)\);', stmt)
    if c and c.group(1).split('.')[0].split('?')[0] not in KEYWORDS and balanced(c.group(2)):
        put('remove_call', indent + '{ }')
    return out


def units(n):
    """The change's source units ("hunks"): [{id, file, start, end, code: [(line no, text)]}], plus what was skipped.
    A unit is a run of added lines of one `git diff -U0` hunk between blank lines, with at least one code line."""
    head = head_of(n)
    changed = set(git('diff', '--name-only', F.BASE, head).splitlines())
    for f in git('ls-tree', '-r', '--name-only', head).splitlines():
        if f.endswith('.tt'):
            F._tt_cache[f] = True
    res, skipped = [], []
    for path in sorted(changed):
        if F.kind(path, changed) != 'source':
            continue
        if not path.endswith('.cs'):
            skipped.append({'file': path, 'reason': 'not C# (no operator for this file type)'})
            continue
        try:
            lines = git('show', f'{head}:{path}').split('\n')
        except subprocess.CalledProcessError:
            skipped.append({'file': path, 'reason': 'deleted by the change'})
            continue
        diff = git('diff', '-U0', '--no-color', F.BASE, head, '--', path)
        for h in re.finditer(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', diff, re.M):
            start, cnt = int(h.group(1)), int(h.group(2) if h.group(2) is not None else 1)
            if cnt == 0:
                skipped.append({'file': path, 'line': start, 'reason': 'lines deleted only (nothing on head to mutate)'})
                continue
            group = []
            for ln in list(range(start, start + cnt)) + [None]:
                if ln is None or not lines[ln - 1].strip():
                    code = [(x, t) for x, t in group if is_code(t)]
                    if code:
                        res.append({'file': path, 'start': group[0][0], 'end': group[-1][0], 'code': code})
                    group = []
                    continue
                group.append((ln, lines[ln - 1]))
    for i, u in enumerate(res, 1):
        u['id'] = f'H{i}'
    return res, skipped


def select(per):
    """At most MAX_MUTANTS from the per-unit candidate lists: round-robin over the units that have candidates (the
    first candidate of each, then the second, ...). When there are more such units than the budget, the units are
    spread evenly over the change (every len/budget-th, in diff order) so one file does not take the whole budget."""
    live = [c for c in per if c]
    if len(live) > MAX_MUTANTS:
        live = [live[i * len(live) // MAX_MUTANTS] for i in range(MAX_MUTANTS)]
    out, r = [], 0
    while len(out) < MAX_MUTANTS and any(len(c) > r for c in live):
        out += [c[r] for c in live if len(c) > r][:MAX_MUTANTS - len(out)]
        r += 1
    return out


def plan(n):
    """(units, skipped, mutants): deterministic, at most MAX_MUTANTS, round-robin over units."""
    us, skipped = units(n)
    per = []
    for u in us:
        cands = [{'file': u['file'], 'line': ln, 'operator': op, 'before': t.rstrip('\r\n'), 'after': new.rstrip('\r\n'), 'hunk': u['id']}
                 for ln, t in u['code'] for op, new in candidates(t)]
        u['candidates'] = len(cands)
        per.append(cands)
    mutants = select(per)
    for k, m in enumerate(mutants, 1):
        m['id'] = f'M{k}'
    return us, skipped, mutants


# ---- run --------------------------------------------------------------------------------------------------------

def apply(wt, m):
    p = os.path.join(wt, m['file'])
    data = open(p, 'rb').read().split(b'\n')
    old = data[m['line'] - 1].decode('utf-8-sig' if m['line'] == 1 else 'utf-8')
    cr = '\r' if old.endswith('\r') else ''
    assert old.rstrip('\r') == m['before'], (old, m['before'])
    bom = b'\xef\xbb\xbf' if m['line'] == 1 and data[0].startswith(b'\xef\xbb\xbf') else b''
    data[m['line'] - 1] = bom + (m['after'] + cr).encode('utf-8')
    open(p, 'wb').write(b'\n'.join(data))


def run(n):
    sp = spec_of(n)
    head = head_of(n)
    wt = f'{F.SRC}/mp-{n}-mt'
    if not os.path.isdir(wt):
        git('worktree', 'add', '--detach', wt, head)
    _, _, mutants = plan(n)
    filt = ';'.join(f'{SG_PROJ}={f}' for f in sp['filters'])
    for m in mutants:
        lab = f"{n}-mt{m['id'][1:]}"
        git('checkout', '--detach', '-f', head, cwd=wt)
        git('checkout', '-f', '--', '.', cwd=wt)
        apply(wt, m)
        d = os.path.join(WORK, 'out', lab)
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
        open(os.path.join(d, 'mutant.diff'), 'w').write(git('diff', cwd=wt))
        json.dump({**m, 'change': n, 'head': head}, open(os.path.join(d, 'mutant.json'), 'w'), indent=1)
        subprocess.run(['bash', os.path.join(HERE, 'run.sh'), lab, wt, SG_PROJ, filt, 'no'], check=True)
        meta = F.read_meta(lab)
        print(n, m['id'], m['operator'], f"{m['file']}:{m['line']}", 'build_rc', meta.get('build_rc'), flush=True)
    git('checkout', '-f', '--', '.', cwd=wt)


# ---- facts ------------------------------------------------------------------------------------------------------

def ran(n):
    return os.path.isdir(os.path.join(WORK, 'out', f'{n}-mt1'))


def judge(n, facts=None):
    """The tests.mutation check for change n from $WORK/out/<n>-mt<k>/, logs copied to evidence/<n>/logs/mutation/.
    `facts` (default: evidence/<n>/facts.json) gives the new tests (tests.fail_without_fix) and head outcomes."""
    sp = spec_of(n)
    cd = os.path.join(F.EVID, n)
    facts = facts or json.load(open(os.path.join(cd, 'facts.json'), encoding='utf-8'))
    fwf = next(c for c in facts['checks'] if c['id'] == 'tests.fail_without_fix')
    new = sorted(t['name'] for t in fwf.get('tests', []) if t.get('new'))
    head_tests = {t['name']: t['outcome'] for t in next(c for c in facts['checks'] if c['id'] == 'tests.targeted')['tests']}
    us, skipped, mutants = plan(n)
    logdir = os.path.join(cd, 'logs', 'mutation')
    if os.path.isdir(logdir):
        shutil.rmtree(logdir)
    recs = []
    for m in mutants:
        lab = f"{n}-mt{m['id'][1:]}"
        d = os.path.join(WORK, 'out', lab)
        meta = F.read_meta(lab)
        rec = {k: m[k] for k in ('id', 'hunk', 'file', 'line', 'operator', 'before', 'after')}
        if meta is None or 'DONE' not in open(os.path.join(d, 'meta.txt')).read():
            recs.append({**rec, 'outcome': 'not_run'})
            continue
        ran = json.load(open(os.path.join(d, 'mutant.json')))
        assert {k: ran[k] for k in rec if k != 'id'} == {k: rec[k] for k in rec if k != 'id'}, f'{lab}: stale run, re-run mutation.py run {n}'
        rec['log'] = [F.copy_log(os.path.join(d, 'build.log'), os.path.join(logdir, f"{m['id']}.build.log"))]
        F.copy_log(os.path.join(d, 'mutant.diff'), os.path.join(logdir, f"{m['id']}.diff"))
        rec['diff'] = f"evidence/{n}/logs/mutation/{m['id']}.diff"
        if meta.get('build_rc') != '0':
            recs.append({**rec, 'outcome': 'not_viable', 'why': 'the mutant does not build'})
            continue
        trx = []
        j = 1
        while f'targeted_{j}_rc' in meta:
            trx += F.parse_trx(os.path.join(d, f'targeted.{j}.trx')) or []
            rec['log'].append(F.copy_log(os.path.join(d, f'targeted.{j}.log'), os.path.join(logdir, f"{m['id']}.test.{j}.log")))
            j += 1
        got = {t['name']: t['outcome'] for t in trx}
        if not trx:
            recs.append({**rec, 'outcome': 'error', 'why': 'no test results'})
            continue
        killed_by = [t for t in new if got.get(t) != 'passed' and head_tests.get(t) == 'passed']
        rec['killed_by'] = killed_by
        rec['existing_tests_failed'] = sorted(t for t, o in got.items() if o == 'failed' and t not in new and head_tests.get(t) == 'passed')
        rec['outcome'] = 'killed' if killed_by else 'survived'
        rec['tests_run'] = len(trx)
        recs.append(rec)
    hunks = []
    for u in us:
        ms = [r for r in recs if r['hunk'] == u['id']]
        judged = [r for r in ms if r['outcome'] in ('killed', 'survived')]
        if any(r['outcome'] == 'killed' for r in ms):
            st = 'killed'
        elif judged:
            st = 'survived'
        else:
            st = 'not_mutated'
        h = {'id': u['id'], 'file': u['file'], 'lines': [u['start'], u['end']], 'code_lines': [ln for ln, _ in u['code']],
             'mutants': [r['id'] for r in ms], 'status': st}
        if st == 'not_mutated':
            h['why'] = ('no operator applies to its lines' if not u['candidates'] else
                        f"left out by the budget ({u['candidates']} candidates; at most {MAX_MUTANTS} mutants per change)" if not ms else
                        'its mutants could not be judged (' + ', '.join(f"{r['id']} {r['outcome']}" for r in ms) + ')')
        hunks.append(h)
    kills = [{'name': t, 'killed': [r['id'] for r in recs if t in r.get('killed_by', [])]} for t in new]
    k = sum(r['outcome'] == 'killed' for r in recs)
    s = sum(r['outcome'] == 'survived' for r in recs)
    other = len(recs) - k - s
    surv = [h for h in hunks if h['status'] == 'survived']
    mutated = [h for h in hunks if h['status'] != 'not_mutated']
    loc = lambda h: f"{h['file'].rsplit('/', 1)[-1]}:{h['lines'][0]}" + (f"-{h['lines'][1]}" if h['lines'][1] != h['lines'][0] else '')  # noqa: E731
    if not k + s:
        status = 'error'
    else:
        status = 'fail' if surv else 'pass'
    summary = (f"{len(recs)} mutants of the changed source lines: {k} killed, {s} survived" + (f", {other} not judged" if other else '')
               + f"; {len(mutated) - len(surv)} of {len(mutated)} mutated hunks have a killed mutant"
               + (f"; surviving hunks: {', '.join(loc(h) for h in surv)}" if surv else '')
               + (f"; {len(hunks) - len(mutated)} hunks not mutated" if len(hunks) > len(mutated) else ''))
    return {'id': CHECK_ID, 'tool': 'evidence/scripts/mutation.py + dotnet test (one mutant at a time, the targeted filter)',
            'tool_version': F.SDK, 'status': status, 'summary': summary,
            'rule': 'killed = at least one new test (new: true in tests.fail_without_fix) fails on the mutant and passed on head; '
                    'pass = every mutated hunk has a killed mutant',
            'operators': OPERATORS, 'max_mutants': MAX_MUTANTS, 'project': F.SG, 'filter': sp['filters'],
            'tests_judged': new,
            'not_covered': 'ExecutionTests/MapModeExecutionTests (SDK 9) are not run against the mutants; files that are not C# are not mutated',
            'hunks': hunks, 'surviving_hunks': [h['id'] for h in surv], 'mutants': recs, 'kills_by_test': kills,
            **({'skipped': skipped} if skipped else {}),
            'log': f'evidence/{n}/logs/mutation/'}


def append_facts(n):
    """Add (or replace) tests.mutation in evidence/<n>/facts.json, every other byte unchanged."""
    p = os.path.join(F.EVID, n, 'facts.json')
    raw = open(p, encoding='utf-8').read()
    facts = json.loads(raw)
    nl = raw.endswith('\n')
    if json.dumps(facts, indent=2) + ('\n' if nl else '') != raw:
        sys.exit(f'{n}: facts.json is not in json.dumps(indent=2) form, so it cannot be rewritten byte-for-byte')
    before = [c for c in facts['checks'] if c['id'] != CHECK_ID]
    chk = judge(n)
    facts['checks'] = before + [chk]
    open(p, 'w', encoding='utf-8').write(json.dumps(facts, indent=2) + ('\n' if nl else ''))
    print(n, chk['status'], chk['summary'])


def main(argv):
    if len(argv) < 2 or argv[0] not in ('plan', 'run', 'facts'):
        sys.exit(__doc__)
    for n in argv[1:]:
        if argv[0] == 'plan':
            us, skipped, ms = plan(n)
            for u in us:
                print(n, u['id'], f"{u['file']}:{u['start']}-{u['end']}", 'candidates', u['candidates'])
            for s in skipped:
                print(n, 'skipped', s)
            for m in ms:
                print(n, m['id'], m['hunk'], f"{m['file'].rsplit('/', 1)[-1]}:{m['line']}", m['operator'], '|', m['before'].strip(), '->', m['after'].strip())
        elif argv[0] == 'run':
            run(n)
        else:
            append_facts(n)


if __name__ == '__main__':
    main(sys.argv[1:])
