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
import os
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"), exist_ok=True)
json.dump(QS, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "coding_qs.json"), "w"))
for q in QS:
    print(q["id"], len(q["hidden"]), [t["out"] for t in q["samples"]])
