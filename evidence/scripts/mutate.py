import sys, json
path, line, before, after, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
lines = open(path, encoding='utf-8-sig').read().split('\n')
raw = open(path,'rb').read()
bom = raw.startswith(b'\xef\xbb\xbf')
orig = lines[line-1]
assert before in orig, (orig, before)
new = orig.replace(before, after)
lines[line-1] = new
data = '\n'.join(lines)
open(path,'wb').write((b'\xef\xbb\xbf' if bom else b'') + data.encode('utf-8'))
json.dump({"file": None, "line": line, "before": orig, "after": new}, open(out,'w'), indent=1)
print(repr(orig)); print(repr(new))
