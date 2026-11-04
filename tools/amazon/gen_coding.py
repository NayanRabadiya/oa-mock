"""Amazon coding questions: statements, reference solutions, brute-force checks and generated tests.
Writes build/coding_qs.json. Run via tools/amazon/build.py."""
import random, json, itertools, sys
from math import comb
random.seed(2026)
MOD = 10**9 + 7

# ---------- Q1: flip a k-window ----------
def flip_ref(s, k):
    n = len(s)
    left = [0]*n; right = [0]*n
    for i in range(n):
        left[i] = (left[i-1] + 1 if i else 1) if s[i] == '1' else 0
    for i in range(n-1, -1, -1):
        right[i] = (right[i+1] + 1 if i < n-1 else 1) if s[i] == '1' else 0
    best = 0
    for i in range(n-k+1):
        a = left[i-1] if i > 0 else 0
        b = right[i+k] if i+k < n else 0
        best = max(best, a + k + b)
    return best

def flip_brute(s, k):
    best = 0
    for i in range(len(s)-k+1):
        t = s[:i] + '1'*k + s[i+k:]
        run = cur = 0
        for c in t:
            cur = cur + 1 if c == '1' else 0
            run = max(run, cur)
        best = max(best, run)
    return best

# ---------- Q2: even blocks of length <= 2 ----------
def even_ref(a):
    e = sum(1 for x in a if x % 2 == 0); o = len(a) - e
    g = o + 1; n = len(a)
    fact = [1]*(n+2)
    for i in range(1, len(fact)): fact[i] = fact[i-1]*i % MOD
    inv = [1]*(n+2); inv[n+1] = pow(fact[n+1], MOD-2, MOD)
    for i in range(n+1, 0, -1): inv[i-1] = inv[i]*i % MOD
    C = lambda x, y: 0 if y < 0 or y > x else fact[x]*inv[y] % MOD * inv[x-y] % MOD
    w = 0
    for t in range(0, e//2 + 1):
        ones = e - 2*t
        if t + ones <= g:
            w += C(g, t) * C(g - t, ones)
    return fact[o] * fact[e] % MOD * (w % MOD) % MOD

def even_brute(a):
    cnt = 0
    for p in itertools.permutations(a):
        run = ok = 1
        cur = 0
        for x in p:
            cur = cur + 1 if x % 2 == 0 else 0
            if cur > 2: ok = 0; break
        cnt += ok
    return cnt % MOD

# ---------- Q3: palindrome-ready subsequences ----------
def pal_ref(s):
    cnt = [0]*26
    for c in s: cnt[ord(c)-97] += 1
    ev = []; od = []
    for c in cnt:
        if c == 0: ev.append(1); od.append(0)
        else: x = pow(2, c-1, MOD); ev.append(x); od.append(x)
    allev = 1
    for x in ev: allev = allev * x % MOD
    # prefix/suffix products (no modular inverse needed)
    pre = [1]*27; suf = [1]*27
    for i in range(26): pre[i+1] = pre[i]*ev[i] % MOD
    for i in range(25, -1, -1): suf[i] = suf[i+1]*ev[i] % MOD
    ans = allev
    for j in range(26):
        ans = (ans + od[j] * pre[j] % MOD * suf[j+1]) % MOD
    return ans

def pal_brute(s):
    n = len(s); c = 0
    for m in range(1 << n):
        cnt = {}
        for i in range(n):
            if m >> i & 1: cnt[s[i]] = cnt.get(s[i], 0) + 1
        if sum(v % 2 for v in cnt.values()) <= 1: c += 1
    return c % MOD

# brute checks
for _ in range(400):
    n = random.randint(1, 12); k = random.randint(1, n)
    s = ''.join(random.choice('01') for _ in range(n))
    assert flip_ref(s, k) == flip_brute(s, k), (s, k)
for _ in range(300):
    n = random.randint(1, 8)
    a = random.sample(range(1, 40), n)
    assert even_ref(a) == even_brute(a), a
for _ in range(300):
    n = random.randint(0, 14)
    s = ''.join(random.choice('abcd'[:random.randint(1, 4)]) for _ in range(n)) or 'a'
    assert pal_ref(s) == pal_brute(s), s
print("brute checks ok")

def T(i, o): return {"in": i, "out": str(o)}

# ---- flip tests
def fin(s, k): return "%s %d" % (s, k)
flip_hidden = []
for s, k in [("0", 1), ("1", 1), ("10101", 1), ("00000", 3), ("1111", 2), ("100001", 4), ("0110011100", 3)]:
    flip_hidden.append(T(fin(s, k), flip_ref(s, k)))
for n, p, k in [(2000, .7, 5), (200000, .5, 1), (200000, .97, 300), (200000, .02, 100000), (200000, .999, 200000)]:
    s = ''.join('1' if random.random() < p else '0' for _ in range(n))
    flip_hidden.append(T(fin(s, k), flip_ref(s, k)))
flip_samples = [
    {"in": "11001 2", "out": str(flip_ref("11001", 2)), "ex": "Flip positions 2–3: 11[00]1 becomes 11111, a run of 5."},
    {"in": "0100110 2", "out": str(flip_ref("0100110", 2)), "ex": "Flipping 0100110 at positions 2–3 gives 0111110, a run of 5. No other window does better."},
]

# ---- even tests
def ein(a): return "%d\n%s" % (len(a), " ".join(map(str, a)))
even_hidden = []
for a in [[2], [7], [2, 4, 6], [2, 4, 6, 1], [1, 3, 5, 7], [2, 4, 6, 8, 10], [2, 4, 6, 8, 1, 3]]:
    even_hidden.append(T(ein(a), even_ref(a)))
def rnd_arr(n, ev_frac):
    seen = set(); out = []
    while len(out) < n:
        x = random.randint(1, 10**9)
        if (x % 2 == 0) != (random.random() < ev_frac): continue
        if x in seen: continue
        seen.add(x); out.append(x)
    return out
for n, f in [(12, .6), (1000, .5), (100000, .66), (200000, .3), (200000, .667)]:
    a = rnd_arr(n, f); even_hidden.append(T(ein(a), even_ref(a)))
# too many evens -> 0
a = rnd_arr(3000, .9); even_hidden.append(T(ein(a), even_ref(a)))
even_samples = [
    {"in": "3\n2 4 6", "out": str(even_ref([2, 4, 6])), "ex": "All three numbers are even, so every arrangement has an even run of length 3."},
    {"in": "4\n1 2 4 6", "out": str(even_ref([1, 2, 4, 6])), "ex": "The odd number must sit inside the evens: E 1 E E or E E 1 E. Each pattern has 3! orders of the evens, so 2 × 6 = 12."},
]

# ---- pal tests
pal_hidden = []
for s in ["a", "ab", "aaaa", "abcabc", "zyxwvutsrqponmlkjihgfedcba", "aabbccddee"]:
    pal_hidden.append(T(s, pal_ref(s)))
for n, alpha in [(1000, 3), (100000, 26), (200000, 1), (200000, 2), (200000, 26)]:
    s = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz'[:alpha]) for _ in range(n))
    pal_hidden.append(T(s, pal_ref(s)))
pal_samples = [
    {"in": "aab", "out": str(pal_ref("aab")), "ex": "The 8 subsequences by position are \"\", a, a, b, aa, ab, ab, aab. All except the two ab can be rearranged into a palindrome (aab → aba), so the answer is 6."},
    {"in": "abc", "out": str(pal_ref("abc")), "ex": "The empty subsequence and the three single letters. Any two or three distinct letters have more than one odd count."},
]

REF = {
 "flip": ("""import sys

def main():
    s, k = sys.stdin.read().split()
    k = int(k); n = len(s)
    left = [0] * n   # 1s ending at i
    right = [0] * n  # 1s starting at i
    for i in range(n):
        left[i] = (left[i-1] + 1 if i else 1) if s[i] == '1' else 0
    for i in range(n - 1, -1, -1):
        right[i] = (right[i+1] + 1 if i < n - 1 else 1) if s[i] == '1' else 0
    best = 0
    for i in range(n - k + 1):
        a = left[i-1] if i else 0
        b = right[i+k] if i + k < n else 0
        best = max(best, a + k + b)
    print(best)

main()
""", """#include <bits/stdc++.h>
using namespace std;
int main() {
    string s; int k; cin >> s >> k;
    int n = s.size();
    vector<int> L(n), R(n);
    for (int i = 0; i < n; i++) L[i] = s[i] == '1' ? (i ? L[i-1] : 0) + 1 : 0;
    for (int i = n - 1; i >= 0; i--) R[i] = s[i] == '1' ? (i + 1 < n ? R[i+1] : 0) + 1 : 0;
    long long best = 0;
    for (int i = 0; i + k <= n; i++) {
        long long a = i ? L[i-1] : 0, b = i + k < n ? R[i+k] : 0;
        best = max(best, a + k + b);
    }
    cout << best << "\\n";
}
"""),
 "evenrun": ("""import sys
MOD = 10**9 + 7

def main():
    d = sys.stdin.read().split()
    n = int(d[0]); a = list(map(int, d[1:1+n]))
    e = sum(1 for x in a if x % 2 == 0); o = n - e
    g = o + 1                       # gaps around the odd numbers
    f = [1] * (n + 2)
    for i in range(1, n + 2): f[i] = f[i-1] * i % MOD
    inv = [1] * (n + 2)
    inv[n+1] = pow(f[n+1], MOD - 2, MOD)
    for i in range(n + 1, 0, -1): inv[i-1] = inv[i] * i % MOD
    C = lambda x, y: 0 if y < 0 or y > x else f[x] * inv[y] % MOD * inv[x-y] % MOD
    w = 0
    for t in range(e // 2 + 1):     # t gaps hold 2 evens, e-2t gaps hold 1
        ones = e - 2 * t
        if t + ones <= g:
            w = (w + C(g, t) * C(g - t, ones)) % MOD
    print(f[o] * f[e] % MOD * w % MOD)

main()
""", """#include <bits/stdc++.h>
using namespace std;
const long long MOD = 1e9 + 7;
long long pw(long long b, long long e) { long long r = 1; b %= MOD; while (e) { if (e & 1) r = r * b % MOD; b = b * b % MOD; e >>= 1; } return r; }
int main() {
    int n; cin >> n;
    int e = 0;
    for (int i = 0; i < n; i++) { long long x; cin >> x; if (x % 2 == 0) e++; }
    int o = n - e, g = o + 1;
    vector<long long> f(n + 2, 1), inv(n + 2, 1);
    for (int i = 1; i <= n + 1; i++) f[i] = f[i-1] * i % MOD;
    inv[n+1] = pw(f[n+1], MOD - 2);
    for (int i = n + 1; i > 0; i--) inv[i-1] = inv[i] * i % MOD;
    auto C = [&](int x, int y) -> long long { if (y < 0 || y > x) return 0; return f[x] * inv[y] % MOD * inv[x-y] % MOD; };
    long long w = 0;
    for (int t = 0; 2 * t <= e; t++) {
        int ones = e - 2 * t;
        if (t + ones <= g) w = (w + C(g, t) * C(g - t, ones)) % MOD;
    }
    cout << f[o] * f[e] % MOD * w % MOD << "\\n";
}
"""),
 "palsub": ("""import sys
MOD = 10**9 + 7

def main():
    s = sys.stdin.read().split()[0]
    cnt = [0] * 26
    for c in s: cnt[ord(c) - 97] += 1
    # picking an even (or odd) number of copies of a letter that appears c > 0 times: 2^(c-1) ways each
    ev = [pow(2, c - 1, MOD) if c else 1 for c in cnt]
    od = [pow(2, c - 1, MOD) if c else 0 for c in cnt]
    pre = [1] * 27; suf = [1] * 27
    for i in range(26): pre[i+1] = pre[i] * ev[i] % MOD
    for i in range(25, -1, -1): suf[i] = suf[i+1] * ev[i] % MOD
    ans = pre[26]                    # every letter even
    for j in range(26):              # exactly letter j odd
        ans = (ans + od[j] * pre[j] % MOD * suf[j+1]) % MOD
    print(ans)

main()
""", """#include <bits/stdc++.h>
using namespace std;
const long long MOD = 1e9 + 7;
int main() {
    string s; cin >> s;
    long long cnt[26] = {0};
    for (char c : s) cnt[c - 'a']++;
    vector<long long> p2(s.size() + 1, 1);
    for (size_t i = 1; i <= s.size(); i++) p2[i] = p2[i-1] * 2 % MOD;
    long long ev[26], od[26];
    for (int i = 0; i < 26; i++) { ev[i] = cnt[i] ? p2[cnt[i]-1] : 1; od[i] = cnt[i] ? p2[cnt[i]-1] : 0; }
    long long pre[27], suf[27]; pre[0] = 1; suf[26] = 1;
    for (int i = 0; i < 26; i++) pre[i+1] = pre[i] * ev[i] % MOD;
    for (int i = 25; i >= 0; i--) suf[i] = suf[i+1] * ev[i] % MOD;
    long long ans = pre[26];
    for (int j = 0; j < 26; j++) ans = (ans + od[j] * pre[j] % MOD * suf[j+1]) % MOD;
    cout << ans << "\\n";
}
"""),
}

QS = [
 {"id": "flip", "type": "code", "title": "Longest Run After One Flip", "diff": "Easy",
  "src": "Amazon SDE-1 Intern OA 2026 · coding section",
  "body": "<p>You are given a binary string <code>log</code> and an integer <code>k</code>. You must choose <b>exactly one</b> substring of length <code>k</code> and change every <code>0</code> inside it to <code>1</code>.</p><p>Print the maximum number of consecutive <code>1</code>s the string can have after this operation.</p>",
  "inp": "One line with the string <code>log</code> and the integer <code>k</code>, separated by a space.",
  "out": "One integer: the longest run of consecutive 1s after the best flip.",
  "cons": ["1 ≤ k ≤ |log| ≤ 2 × 10<sup>5</sup>", "<code>log</code> contains only 0 and 1"],
  "samples": flip_samples, "hidden": flip_hidden, "ref": REF["flip"][0], "refcpp": REF["flip"][1],
  "lc": "1004 Max Consecutive Ones III", "lcurl": "https://leetcode.com/problems/max-consecutive-ones-iii/"},
 {"id": "palsub", "type": "code", "title": "Palindrome-Ready Subsequences", "diff": "Medium",
  "src": "Amazon 2026 Intern OA (IIIT Delhi, 4 July)",
  "body": "<p>You are given a string <code>s</code> of length <code>n</code> made of lowercase English letters. Count the subsequences of <code>s</code> whose letters can be rearranged into a palindrome. The empty subsequence counts as a palindrome.</p><p>Subsequences are counted by the positions chosen, so two equal strings taken from different positions are different subsequences. Print the count modulo 10<sup>9</sup> + 7.</p>",
  "inp": "One line with the string <code>s</code>.",
  "out": "One integer: the count modulo 10<sup>9</sup> + 7.",
  "cons": ["1 ≤ n ≤ 2 × 10<sup>5</sup>", "<code>s</code> contains only lowercase English letters"],
  "samples": pal_samples, "hidden": pal_hidden, "ref": REF["palsub"][0], "refcpp": REF["palsub"][1],
  "lc": "1177 Can Make Palindrome from Substring", "lcurl": "https://leetcode.com/problems/can-make-palindrome-from-substring/"},
 {"id": "evenrun", "type": "code", "title": "Even Blocks of At Most Two", "diff": "Hard",
  "src": "Amazon 2026 Intern OA (IIIT Delhi, 4 July)",
  "body": "<p>You are given an array <code>A</code> of <code>n</code> <b>distinct</b> positive integers. Count the rearrangements (permutations) of <code>A</code> in which every contiguous block made only of even numbers has length at most <code>2</code>. In other words, no three even numbers may stand next to each other.</p><p>Print the count modulo 10<sup>9</sup> + 7.</p>",
  "inp": "The first line contains <code>n</code>. The second line contains the <code>n</code> elements of <code>A</code>.",
  "out": "One integer: the number of valid rearrangements modulo 10<sup>9</sup> + 7.",
  "cons": ["1 ≤ n ≤ 2 × 10<sup>5</sup>", "1 ≤ A[i] ≤ 10<sup>9</sup>", "All elements are distinct"],
  "samples": even_samples, "hidden": even_hidden, "ref": REF["evenrun"][0], "refcpp": REF["evenrun"][1],
  "lc": "1220 Count Vowels Permutation (counting with run limits)", "lcurl": "https://leetcode.com/problems/count-vowels-permutation/"},
]

# ========================================================================
#  Online coding set 2024 (Amazon FTE / online OA, HackerRank test rfe1p4jtmt)
#  Five more coding questions. Each has a reference + a brute force that are
#  cross-checked on small inputs; the LeetCode-style stubs/drivers/refs live
#  in fnstyle.py and overwrite ref/refcpp below.
# ========================================================================

# ---------- Q4: pairs whose cost sum is divisible by x ----------
def findpairs_ref(x, cost):
    from collections import Counter
    c = Counter(v % x for v in cost)
    ans = 0
    for r, cnt in c.items():
        s = (x - r) % x
        if s == r:
            ans += cnt * (cnt - 1) // 2
        elif r < s:
            ans += cnt * c.get(s, 0)
    return ans

def findpairs_brute(x, cost):
    n = len(cost)
    return sum(1 for i in range(n) for j in range(i + 1, n) if (cost[i] + cost[j]) % x == 0)

# ---------- Q5: minimise the maximum load after adding extra units ----------
def parcels_ref(parcels, extra):
    lo, hi = max(parcels), max(parcels) + extra
    def room(L):
        s = 0
        for p in parcels:
            if p < L:
                s += L - p
                if s >= extra:
                    return s
        return s
    while lo < hi:
        mid = (lo + hi) // 2
        if room(mid) >= extra:
            hi = mid
        else:
            lo = mid + 1
    return lo

def parcels_brute(parcels, extra):
    import heapq
    h = list(parcels); heapq.heapify(h)
    for _ in range(extra):
        heapq.heapreplace(h, h[0] + 1)
    return max(h)

# ---------- Q6: the largest potential outlier ----------
def outlier_ref(arr):
    from collections import Counter
    S = sum(arr); freq = Counter(arr)
    best = None
    for o in arr:
        t = S - o
        if t % 2:
            continue
        m = t // 2
        ok = (freq[m] >= 2) if m == o else (freq[m] >= 1)
        if ok:
            best = o if best is None else max(best, o)
    return best

def outlier_brute(arr):
    n = len(arr); best = None
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            rest = sum(arr[k] for k in range(n) if k != i and k != j)
            if rest == arr[j]:
                best = arr[i] if best is None else max(best, arr[i])
    return best

# ---------- Q7: players capable of defeating every other player ----------
def _maxwin(X, Y):
    best = 0
    for p in itertools.permutations(Y):
        best = max(best, sum(1 for u, v in zip(X, p) if u > v))
    return best

def winners_ref(a, b, c):
    n = len(a)
    pls = [tuple(sorted((a[i], b[i], c[i]))) for i in range(n)]
    lo = [p[0] for p in pls]; mid = [p[1] for p in pls]
    def top2(v):
        i1 = i2 = -1
        for i, x in enumerate(v):
            if i1 < 0 or x > v[i1]:
                i2 = i1; i1 = i
            elif i2 < 0 or x > v[i2]:
                i2 = i
        return i1, i2
    l1, l2 = top2(lo); m1, m2 = top2(mid)
    cnt = 0
    for i, p in enumerate(pls):
        max_lo = lo[l2] if i == l1 else lo[l1]
        max_mid = mid[m2] if i == m1 else mid[m1]
        if p[1] > max_lo and p[2] > max_mid:
            cnt += 1
    return cnt

def winners_brute(a, b, c):
    n = len(a); pls = [(a[i], b[i], c[i]) for i in range(n)]
    return sum(1 for i in range(n)
               if all(_maxwin(pls[i], pls[j]) >= 2 for j in range(n) if j != i))

# ---------- Q8: fewest '?' in a pattern intersecting all patterns ----------
def qmarks_ref(patterns):
    m = len(patterns[0]); cnt = 0
    for j in range(m):
        if len({p[j] for p in patterns if p[j] != '?'}) >= 2:
            cnt += 1
    return cnt

def qmarks_brute(patterns):
    m = len(patterns[0]); total = 0
    for j in range(m):
        col = [p[j] for p in patterns]
        ok = any(all(c == '?' or c == ch for c in col)
                 for ch in 'abcdefghijklmnopqrstuvwxyz')
        total += 0 if ok else 1
    return total

# brute checks for the five
for _ in range(500):
    _n = random.randint(1, 12); _x = random.randint(1, 15)
    _cost = [random.randint(1, 40) for _ in range(_n)]
    assert findpairs_ref(_x, _cost) == findpairs_brute(_x, _cost)
for _ in range(500):
    _p = [random.randint(1, 15) for _ in range(random.randint(1, 8))]
    _e = random.randint(0, 30)
    assert parcels_ref(_p, _e) == parcels_brute(_p, _e)
for _ in range(500):
    _sp = [random.randint(-8, 8) for _ in range(random.randint(2, 6))]
    _arr = _sp + [sum(_sp), random.randint(-20, 20)]; random.shuffle(_arr)
    assert outlier_ref(_arr) == outlier_brute(_arr)
for _ in range(500):
    _n = random.randint(2, 6); _a = []; _b = []; _c = []
    for _ in range(_n):
        _t = random.sample(range(1, 40), 3); _a.append(_t[0]); _b.append(_t[1]); _c.append(_t[2])
    assert winners_ref(_a, _b, _c) == winners_brute(_a, _b, _c)
for _ in range(500):
    _m = random.randint(1, 7); _pat = ["".join(random.choice("abcd??") for _ in range(_m))
                                       for _ in range(random.randint(1, 6))]
    assert qmarks_ref(_pat) == qmarks_brute(_pat)
print("online-2024 brute checks ok")

# ---- findPairs tests: STDIN = x \n n \n cost[0..n-1]
def fp_in(x, cost): return "%d\n%d\n%s" % (x, len(cost), "\n".join(map(str, cost)))
findpairs_hidden = []
for x, cost in [(1, [1, 2, 3, 4]), (2, [2]), (5, [5, 10, 15, 20]), (7, [1, 6, 8, 13, 15]),
                (3, [3, 6, 9, 3, 6]), (1000000000, [1000000000, 1000000000])]:
    findpairs_hidden.append(T(fp_in(x, cost), findpairs_ref(x, cost)))
for n, x, hi in [(2000, 97, 1000), (100000, 1, 1000000000), (100000, 2, 1000000000),
                 (100000, 1000000000, 1000000000), (100000, 2000000000, 1000000000)]:
    cost = [random.randint(1, hi) for _ in range(n)]
    findpairs_hidden.append(T(fp_in(x, cost), findpairs_ref(x, cost)))
findpairs_samples = [
    {"in": fp_in(60, [31, 25, 85, 29, 35]), "out": str(findpairs_ref(60, [31, 25, 85, 29, 35])),
     "ex": "The pairs that sum to a multiple of 60 are (31, 29), (25, 35) and (85, 35), so the answer is 3."},
    {"in": fp_in(10, [3, 7, 27, 23]), "out": str(findpairs_ref(10, [3, 7, 27, 23])),
     "ex": "(3, 7), (3, 27), (23, 7) and (23, 27) each sum to a multiple of 10, so the answer is 4."},
]

# ---- getMinMaxParcels tests: STDIN = n \n parcels[0..n-1] \n extra
def pc_in(p, e): return "%d\n%s\n%d" % (len(p), "\n".join(map(str, p)), e)
parcels_hidden = []
for p, e in [([1], 3), ([5, 5, 5], 0), ([1, 1, 1, 1], 4), ([10, 1], 5),
             ([7, 5, 1, 9, 1], 25), ([1000000000], 1000000000000)]:
    parcels_hidden.append(T(pc_in(p, e), parcels_ref(p, e)))
for n, hi, e in [(1000, 1000, 50000), (100000, 1, 1000000000), (100000, 1000000000, 1000000000000),
                 (100000, 1000000, 1), (100000, 1000000000, 1)]:
    p = [random.randint(1, hi) for _ in range(n)]
    parcels_hidden.append(T(pc_in(p, e), parcels_ref(p, e)))
parcels_samples = [
    {"in": pc_in([1, 2, 3], 3), "out": str(parcels_ref([1, 2, 3], 3)),
     "ex": "Give 2 extra to the first agent and 1 to the second: loads become 3, 3, 3. The maximum is 3."},
    {"in": pc_in([1], 3), "out": str(parcels_ref([1], 3)),
     "ex": "With one agent, all 3 extra parcels go to it, so it delivers 1 + 3 = 4."},
]

# ---- getOutlierValue tests: STDIN = n \n arr[0..n-1]
def ov_in(a): return "%d\n%s" % (len(a), "\n".join(map(str, a)))
def mk_outlier(specials, outlier):
    arr = list(specials) + [sum(specials), outlier]
    random.shuffle(arr)
    return arr
outlier_hidden = []
for arr in [mk_outlier([1, 2, 3, 4], 100), mk_outlier([-5, -5, -5], 7),
            mk_outlier([10], 10), mk_outlier([2, 3], -9), mk_outlier([6, 6, 6, 6], 25)]:
    outlier_hidden.append(T(ov_in(arr), outlier_ref(arr)))
for n in [1000, 100000]:
    sp = [random.randint(-1000000, 1000000) for _ in range(n - 2)]
    arr = mk_outlier(sp, random.randint(-1000000, 1000000))
    outlier_hidden.append(T(ov_in(arr), outlier_ref(arr)))
outlier_samples = [
    {"in": ov_in([4, 1, 3, 16, 2, 10]), "out": str(outlier_ref([4, 1, 3, 16, 2, 10])),
     "ex": "Removing 16 leaves [4, 1, 3, 2, 10] whose first four sum to 10, and removing 4 leaves "
           "[1, 3, 16, 2, 10] whose others sum to 16. Both 16 and 4 are potential outliers; the greater is 16."},
    {"in": ov_in([2, 3, 4, 2]), "out": str(outlier_ref([2, 3, 4, 2]) if outlier_ref([2, 3, 4, 2]) is not None else 0),
     "ex": "The specials [2, 2] sum to 4, leaving 3 as the outlier."},
]

# ---- findCapableWinners tests: STDIN = n \n a[..] \n n \n b[..] \n n \n c[..]
def cw_in(a, b, c):
    parts = [str(len(a))] + list(map(str, a)) + [str(len(b))] + list(map(str, b)) + [str(len(c))] + list(map(str, c))
    return "\n".join(parts)
winners_hidden = []
for a, b, c in [([4, 2], [8, 5], [10, 12]),
                ([3, 4, 1, 16], [2, 11, 5, 6], [8, 7, 9, 10]),
                ([9, 4, 2], [5, 12, 10], [11, 3, 13]),
                ([1, 10], [2, 20], [3, 30]),
                ([5, 5], [5, 5], [5, 5])]:
    # keep each player's three boosters distinct
    winners_hidden.append(T(cw_in(a, b, c), winners_ref(a, b, c)))
def rnd_players(n):
    a = []; b = []; c = []
    for _ in range(n):
        t = random.sample(range(1, 1000000000), 3)
        a.append(t[0]); b.append(t[1]); c.append(t[2])
    return a, b, c
for n in [500, 100000]:
    a, b, c = rnd_players(n)
    winners_hidden.append(T(cw_in(a, b, c), winners_ref(a, b, c)))
winners_samples = [
    {"in": cw_in([4, 2], [8, 5], [10, 12]), "out": str(winners_ref([4, 2], [8, 5], [10, 12])),
     "ex": "Player 1 has {4, 8, 10} and Player 2 has {2, 5, 12}. Player 1 wins with 4>2, 8>5; Player 2 wins "
           "with 5>4, 12>8. Each defeats the other in 2 of 3 rounds, so both are capable: the answer is 2."},
    {"in": cw_in([3, 4, 1, 16], [2, 11, 5, 6], [8, 7, 9, 10]),
     "out": str(winners_ref([3, 4, 1, 16], [2, 11, 5, 6], [8, 7, 9, 10])),
     "ex": "The players hold {3,2,8}, {4,11,7}, {1,5,9} and {16,6,10}. Only the players with boosters "
           "{4,11,7} and {16,6,10} beat every other player in at least 2 of the 3 rounds, so the answer is 2."},
]

# ---- minQuestionMarks tests: STDIN = n \n pattern[0..n-1]
def qm_in(pats): return "%d\n%s" % (len(pats), "\n".join(pats))
qmarks_hidden = []
for pats in [["abc"], ["a?c", "abc", "a?c"], ["ab", "cd"], ["????", "abcd"],
             ["hello", "he??o", "h?llo"], ["ax", "bx", "cx", "dx"]]:
    qmarks_hidden.append(T(qm_in(pats), qmarks_ref(pats)))
# a large block: many patterns of equal length, some columns conflicting
big_m = 1000
base = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(big_m))
pats = []
for _ in range(100):
    row = list(base)
    for _ in range(50):
        k = random.randrange(big_m)
        row[k] = random.choice("??abcdefghijklmnopqrstuvwxyz")
    pats.append("".join(row))
qmarks_hidden.append(T(qm_in(pats), qmarks_ref(pats)))
qmarks_samples = [
    {"in": qm_in(["ha???rrank", "?a?ke?bank"]), "out": str(qmarks_ref(["ha???rrank", "?a?ke?bank"])),
     "ex": "Only the position holding r vs b differs between the two patterns, so one '?' there (for example "
           "hacker?ank) intersects both. Every other position has a single forced letter. The answer is 1."},
    {"in": qm_in(["ax", "bx", "cx"]), "out": str(qmarks_ref(["ax", "bx", "cx"])),
     "ex": "The first column holds three different letters (a, b, c), so it needs a '?'. The second column is "
           "x everywhere. One '?' is enough."},
]

QS += [
 {"id": "findpairs", "type": "code", "title": "Pairs With Sum Divisible by X", "diff": "Easy",
  "src": "Amazon 2024 online OA (HackerRank)",
  "body": "<p>Amazon offers a discount on every purchase of a <b>pair</b> of products whose cost sum is divisible by <code>x</code>. Given the cost of <code>n</code> products in <code>cost</code>, count the pairs <code>(i, j)</code> with <code>i &lt; j</code> for which <code>cost[i] + cost[j]</code> is divisible by <code>x</code>.</p>",
  "inp": "The first line is <code>x</code>. The second line is <code>n</code>. Each of the next <code>n</code> lines is one <code>cost[i]</code>.",
  "out": "The number of pairs whose cost sum is divisible by <code>x</code>.",
  "cons": ["1 ≤ x ≤ 2 × 10<sup>9</sup>", "1 ≤ n ≤ 10<sup>5</sup>", "1 ≤ cost[i] ≤ 10<sup>9</sup>"],
  "samples": findpairs_samples, "hidden": findpairs_hidden, "ref": "", "refcpp": "",
  "lc": "1010 Pairs of Songs With Total Durations Divisible by 60",
  "lcurl": "https://leetcode.com/problems/pairs-of-songs-with-total-durations-divisible-by-60/"},
 {"id": "parcels", "type": "code", "title": "Minimise the Maximum Load", "diff": "Medium",
  "src": "Amazon 2024 online OA (HackerRank)",
  "body": "<p>Amazon distributes parcels among delivery agents. Initially the <code>i</code>-th of <code>n</code> agents is assigned <code>parcels[i]</code> parcels, and there are <code>extra_parcels</code> more that must all be assigned. Distribute the extra parcels so that the <b>maximum</b> number of parcels assigned to any one agent is as small as possible, and find that minimum possible maximum.</p>",
  "inp": "The first line is <code>n</code>. Each of the next <code>n</code> lines is one <code>parcels[i]</code>. The final line is <code>extra_parcels</code>.",
  "out": "The minimum possible value of the maximum load on any agent.",
  "cons": ["1 ≤ n ≤ 10<sup>5</sup>", "1 ≤ parcels[i] ≤ 10<sup>9</sup>", "0 ≤ extra_parcels ≤ 10<sup>12</sup>"],
  "samples": parcels_samples, "hidden": parcels_hidden, "ref": "", "refcpp": "",
  "lc": "1011 Capacity To Ship Packages Within D Days (binary search on the answer)",
  "lcurl": "https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/"},
 {"id": "outlier", "type": "code", "title": "Largest Potential Outlier", "diff": "Easy",
  "src": "Amazon 2024 online OA (HackerRank)",
  "body": "<p>An array of <code>n</code> integers was built from <code>n - 2</code> normal numbers plus their <b>sum</b> (that is <code>n - 1</code> values), and then one more value, the <b>outlier</b>, was added. The outlier is neither one of the normal numbers nor their sum. More than one value may qualify as the outlier; find the <b>greatest</b> such value.</p><p class=\"muted\">It is guaranteed that a valid outlier exists.</p>",
  "inp": "The first line is <code>n</code>. Each of the next <code>n</code> lines is one array element.",
  "out": "The greatest value that can be the outlier.",
  "cons": ["3 ≤ n ≤ 10<sup>5</sup>", "-10<sup>6</sup> ≤ arr[i] ≤ 10<sup>6</sup>", "A valid outlier is guaranteed to exist"],
  "samples": outlier_samples, "hidden": outlier_hidden, "ref": "", "refcpp": "",
  "lc": "3371 Identify the Largest Outlier in an Array",
  "lcurl": "https://leetcode.com/problems/identify-the-largest-outlier-in-an-array/"},
 {"id": "winners", "type": "code", "title": "Capable Tournament Winners", "diff": "Medium",
  "src": "Amazon 2024 online OA (HackerRank)",
  "body": "<p>In a tournament each game has 3 rounds and every player holds exactly three power boosters, used at most once per game; the higher booster wins a round. The <code>i</code>-th of <code>n</code> players has boosters <code>(power_a[i], power_b[i], power_c[i])</code>.</p><p>A player <b>X</b> is capable of defeating player <b>Y</b> if, choosing the order of boosters, X can win <b>at least 2</b> of the 3 rounds. Count the players who are capable of defeating <b>every</b> other player.</p>",
  "inp": "Three blocks, one per booster set. Each block is <code>n</code> on its own line followed by the <code>n</code> values of that set (<code>power_a</code>, then <code>power_b</code>, then <code>power_c</code>).",
  "out": "The number of players capable of defeating all other players.",
  "cons": ["2 ≤ n ≤ 10<sup>5</sup>", "1 ≤ power_a[i], power_b[i], power_c[i] ≤ 10<sup>9</sup>", "Each player's three boosters are distinct"],
  "samples": winners_samples, "hidden": winners_hidden, "ref": "", "refcpp": "",
  "lc": "870 Advantage Shuffle (greedy higher-than matching)",
  "lcurl": "https://leetcode.com/problems/advantage-shuffle/"},
 {"id": "qmarks", "type": "code", "title": "Fewest Wildcards in a Common Pattern", "diff": "Medium",
  "src": "Amazon 2024 online OA (HackerRank)",
  "body": "<p>A pattern is a string of lowercase letters and <code>?</code> wildcards (each <code>?</code> matches any one letter). Two patterns <b>intersect</b> if the wildcards can be filled so both produce the same string. Given <code>n</code> patterns of equal length, find the minimum number of <code>?</code> a pattern can contain while still intersecting <b>all</b> of them.</p>",
  "inp": "The first line is <code>n</code>. Each of the next <code>n</code> lines is one pattern.",
  "out": "The fewest <code>?</code> characters a pattern intersecting all of them can have.",
  "cons": ["1 ≤ n ≤ 10<sup>4</sup>", "All patterns have the same length m, 1 ≤ m ≤ 10<sup>3</sup>", "Patterns use lowercase letters and <code>?</code>"],
  "samples": qmarks_samples, "hidden": qmarks_hidden, "ref": "", "refcpp": "",
  "lc": None, "lcurl": None},
]

import os
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"), exist_ok=True)
json.dump(QS, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "coding_qs.json"), "w"))
for q in QS:
    print(q["id"], len(q["hidden"]), [t["out"] for t in q["samples"]])
