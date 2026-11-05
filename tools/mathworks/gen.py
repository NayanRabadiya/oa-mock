#!/usr/bin/env python3
"""Builds data/mathworks/questions/*.json.

    python3 tools/mathworks/gen.py

Each question's tests come from its Python reference. Before writing anything, the
reference is compared with a brute force on a few thousand small random inputs, so the
expected outputs are not just "whatever the reference printed".
"""
import json, os, random, subprocess, sys
from collections import Counter
from itertools import product

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "data", "mathworks", "questions")
SRC = "MathWorks OA, IIT Bombay, 2026"
rng = random.Random(2026)


def run_py(code, inp):
    r = subprocess.run([sys.executable, "-c", code], input=inp, capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


# ---------------------------------------------------------------- 1. minids
MINIDS_PY = r'''import sys
from collections import Counter

def main():
    t = sys.stdin.read().split()
    n, m = int(t[0]), int(t[1])
    freq = sorted(Counter(t[2:2 + n]).values())
    left = len(freq)
    for f in freq:
        if m < f:
            break
        m -= f
        left -= 1
    print(left)

main()
'''
MINIDS_CPP = r'''#include <bits/stdc++.h>
using namespace std;
int main(){
    int n; long long m; cin >> n >> m;
    unordered_map<long long,int> cnt; cnt.reserve(n * 2 + 1);
    for (int i = 0; i < n; i++){ long long x; cin >> x; cnt[x]++; }
    vector<int> f; for (auto &p : cnt) f.push_back(p.second);
    sort(f.begin(), f.end());
    int left = f.size();
    for (int x : f){ if (m < x) break; m -= x; left--; }
    cout << left << "\n";
}
'''


def minids_brute(arr, m):
    best = len(arr)
    for drop in product([0, 1], repeat=len(arr)):
        if sum(drop) == m:
            best = min(best, len({a for a, d in zip(arr, drop) if not d}))
    return best


def minids_in(arr, m):
    return "%d %d\n%s\n" % (len(arr), m, " ".join(map(str, arr)))


# ---------------------------------------------------------------- 2. twodenom
TWODENOM_PY = r'''import sys

def main():
    t = sys.stdin.read().split(); p = 0
    n, k = int(t[0]), int(t[1]); p = 2
    arr = list(map(int, t[p:p + n])); p += n
    q = int(t[p]); p += 1
    qs = list(map(int, t[p:p + q]))
    best = {0: 0}                      # amount -> fewest notes using ONE value
    for v in arr:
        for c in range(1, k + 1):
            s = v * c
            if best.get(s, k + 1) > c:
                best[s] = c
    res = []
    for x in qs:
        ans = best.get(x, k + 1)
        for v in arr:
            for a in range(1, k + 1):
                r = x - v * a
                if r < 0:
                    break
                b = best.get(r)
                if b is not None and a + b < ans:
                    ans = a + b
        res.append(ans if ans <= k else -1)
    print(" ".join(map(str, res)))

main()
'''
TWODENOM_CPP = r'''#include <bits/stdc++.h>
using namespace std;
int main(){
    int n, k; cin >> n >> k;
    vector<long long> a(n); for (auto &x : a) cin >> x;
    int q; cin >> q;
    unordered_map<long long,int> best; best.reserve(n * k * 2 + 1); best[0] = 0;
    for (long long v : a) for (int c = 1; c <= k; c++){
        auto it = best.find(v * c);
        if (it == best.end() || it->second > c) best[v * c] = c;
    }
    for (int i = 0; i < q; i++){
        long long x; cin >> x;
        int ans = k + 1;
        auto it0 = best.find(x); if (it0 != best.end()) ans = it0->second;
        for (long long v : a) for (int c = 1; c <= k; c++){
            long long r = x - v * c; if (r < 0) break;
            auto it = best.find(r);
            if (it != best.end() && c + it->second < ans) ans = c + it->second;
        }
        cout << (ans <= k ? ans : -1) << (i + 1 < q ? " " : "\n");
    }
}
'''


def twodenom_brute(arr, k, x):
    best = -1
    for i in range(len(arr)):
        for j in range(len(arr)):
            for a in range(k + 1):
                for b in range(k + 1 - a):
                    if a * arr[i] + b * arr[j] == x and (best == -1 or a + b < best):
                        best = a + b
    return best


def twodenom_in(arr, k, qs):
    return "%d %d\n%s\n%d\n%s\n" % (len(arr), k, " ".join(map(str, arr)), len(qs), " ".join(map(str, qs)))


# ---------------------------------------------------------------- 3. majparts
MAJPARTS_PY = r'''import sys
from collections import Counter

def main():
    t = sys.stdin.read().split()
    n = int(t[0])
    freq = sorted(Counter(t[1:1 + n]).values(), reverse=True)
    covered = 0
    for groups, f in enumerate(freq, 1):
        covered += 2 * f - 1         # f copies + up to f - 1 other elements
        if covered >= n:
            print(groups)
            return

main()
'''
MAJPARTS_CPP = r'''#include <bits/stdc++.h>
using namespace std;
int main(){
    int n; cin >> n;
    unordered_map<long long,int> cnt; cnt.reserve(n * 2 + 1);
    for (int i = 0; i < n; i++){ long long x; cin >> x; cnt[x]++; }
    vector<int> f; for (auto &p : cnt) f.push_back(p.second);
    sort(f.rbegin(), f.rend());
    long long covered = 0;
    for (size_t g = 0; g < f.size(); g++){
        covered += 2LL * f[g] - 1;
        if (covered >= n){ cout << g + 1 << "\n"; return 0; }
    }
}
'''


def majparts_brute(arr):
    n = len(arr)

    def ok(group):
        return max(Counter(group).values()) * 2 > len(group)

    best = n
    # assign every element a group label (restricted growth strings)
    def rec(i, labels, g):
        nonlocal best
        if g >= best:
            return
        if i == n:
            groups = [[arr[j] for j in range(n) if labels[j] == x] for x in range(g)]
            if all(ok(gr) for gr in groups):
                best = g
            return
        for x in range(g + 1):
            labels.append(x)
            rec(i + 1, labels, max(g, x + 1))
            labels.pop()
    rec(0, [], 0)
    return best


def majparts_in(arr):
    return "%d\n%s\n" % (len(arr), " ".join(map(str, arr)))


# ---------------------------------------------------------------- 4. palsubs
PALSUBS_PY = r'''import sys

def count(s):
    seen = {0: 1}; mask = 0; total = 0
    for ch in s:
        mask ^= 1 << (ord(ch) - 97)
        total += seen.get(mask, 0)               # every letter even
        for b in range(26):                       # exactly one letter odd
            total += seen.get(mask ^ (1 << b), 0)
        seen[mask] = seen.get(mask, 0) + 1
    return total

def main():
    t = sys.stdin.read().split()
    print("\n".join(str(count(s)) for s in t[1:1 + int(t[0])]))

main()
'''
PALSUBS_CPP = r'''#include <bits/stdc++.h>
using namespace std;
int main(){
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int T; cin >> T;
    while (T--){
        string s; cin >> s;
        unordered_map<int,long long> seen; seen.reserve(s.size() * 2 + 2); seen[0] = 1;
        int mask = 0; long long total = 0;
        for (char ch : s){
            mask ^= 1 << (ch - 'a');
            auto it = seen.find(mask); if (it != seen.end()) total += it->second;
            for (int b = 0; b < 26; b++){
                auto jt = seen.find(mask ^ (1 << b)); if (jt != seen.end()) total += jt->second;
            }
            seen[mask]++;
        }
        cout << total << "\n";
    }
}
'''


def palsubs_brute(s):
    c = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if sum(v % 2 for v in Counter(s[i:j]).values()) <= 1:
                c += 1
    return c


def palsubs_in(ss):
    return "%d\n%s\n" % (len(ss), "\n".join(ss))


# ---------------------------------------------------------------- 5. beauty
BEAUTY_PY = r'''import sys

def tri(x):
    return x * (x + 1) // 2

def main():
    s = sys.stdin.read().split()[0]
    n = len(s)
    # Split into letter runs and the dots between them.
    runs = []                     # [letter, length]
    gaps = []                     # dots before runs[i] (gaps[0] = leading dots)
    dots = 0
    for ch in s:
        if ch == '.':
            dots += 1
        elif runs and runs[-1][0] == ch:      # same letter on both sides of the dots: fill them all
            runs[-1][1] += dots + 1; dots = 0
        else:
            gaps.append(dots); runs.append([ch, 1]); dots = 0
    if not runs:
        print(tri(n)); return
    runs[0][1] += gaps[0]; runs[-1][1] += dots    # leading / trailing dots join the nearest run
    # A gap between different letters goes wholly to one side (the score is convex).
    # dp[g] = best score of runs before i, where g = dots run i already took from its left gap.
    m = len(runs)
    dp = {0: 0}
    for i in range(m):
        right = gaps[i + 1] if i + 1 < m else 0
        nd = {}
        for took, val in dp.items():
            for give_left in ((True, False) if right else (False,)):
                length = runs[i][1] + took + (right if give_left else 0)
                key = 0 if give_left else right
                v = val + tri(length)
                if nd.get(key, -1) < v:
                    nd[key] = v
        dp = nd
    print(max(dp.values()))

main()
'''
BEAUTY_CPP = r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
ll tri(ll x){ return x * (x + 1) / 2; }
int main(){
    string s; cin >> s; ll n = s.size();
    vector<ll> len, gap; vector<char> let; ll dots = 0;
    for (char ch : s){
        if (ch == '.') dots++;
        else if (!let.empty() && let.back() == ch){ len.back() += dots + 1; dots = 0; }
        else { gap.push_back(dots); let.push_back(ch); len.push_back(1); dots = 0; }
    }
    if (let.empty()){ cout << tri(n) << "\n"; return 0; }
    int m = let.size(); len[0] += gap[0]; len[m - 1] += dots;
    // a = best if run i took nothing from its left gap, b = best if it took the whole gap
    ll a = 0, b = LLONG_MIN;
    for (int i = 0; i < m; i++){
        ll right = (i + 1 < m) ? gap[i + 1] : 0, L = gap[i];
        ll na = LLONG_MIN, nb = LLONG_MIN;
        for (int t = 0; t < 2; t++){
            ll val = t ? b : a; if (val == LLONG_MIN) continue;
            ll base = len[i] + (t ? L : 0);
            na = max(na, val + tri(base + right));          // right gap given to this run
            if (right) nb = max(nb, val + tri(base));       // right gap given to the next run
        }
        a = na; b = nb;
    }
    cout << max(a, b) << "\n";
}
'''


def beauty_score(t):
    c, i = 0, 0
    while i < len(t):
        j = i
        while j < len(t) and t[j] == t[i]:
            j += 1
        c += (j - i) * (j - i + 1) // 2
        i = j
    return c


def beauty_brute(s):
    letters = sorted(set(s) - {'.'}) + [c for c in "xyz" if c not in s][:1]
    idx = [i for i, ch in enumerate(s) if ch == '.']
    best = 0
    for fill in product(letters, repeat=len(idx)):
        t = list(s)
        for i, ch in zip(idx, fill):
            t[i] = ch
        best = max(best, beauty_score(t))
    return best


# ---------------------------------------------------------------- verification
def verify():
    print("brute-force cross-check ...")
    for _ in range(400):
        n = rng.randint(1, 10); arr = [rng.randint(1, 4) for _ in range(n)]; m = rng.randint(0, n)
        assert run_py(MINIDS_PY, minids_in(arr, m)) == str(minids_brute(arr, m)), (arr, m)
    for _ in range(300):
        arr = sorted(rng.sample(range(1, 40), rng.randint(1, 5))); k = rng.randint(1, 6)
        qs = [rng.randint(1, 150) for _ in range(rng.randint(1, 8))]
        want = " ".join(str(twodenom_brute(arr, k, x)) for x in qs)
        assert run_py(TWODENOM_PY, twodenom_in(arr, k, qs)) == want, (arr, k, qs)
    for _ in range(300):
        n = rng.randint(1, 8); arr = [rng.randint(1, rng.randint(1, 5)) for _ in range(n)]
        assert run_py(MAJPARTS_PY, majparts_in(arr)) == str(majparts_brute(arr)), arr
    for _ in range(100):
        ss = ["".join(rng.choice("abc"[:rng.randint(1, 3)]) for _ in range(rng.randint(1, 12))) for _ in range(5)]
        want = "\n".join(str(palsubs_brute(s)) for s in ss)
        assert run_py(PALSUBS_PY, palsubs_in(ss)) == want, ss
    for _ in range(500):
        s = "".join(rng.choice("ab..c."[:rng.choice([3, 4, 6])]) for _ in range(rng.randint(1, 9)))
        assert run_py(BEAUTY_PY, s + "\n") == str(beauty_brute(s)), s
    print("ok")


# ---------------------------------------------------------------- tests
def tests_minids():
    T = [([5, 5, 5], 1), ([1, 2, 3, 4, 5], 0), ([7], 1), ([2, 2, 1, 1, 1, 3], 6), ([4, 4, 9, 9, 9, 1], 3),
         ([10, 20, 20, 30, 30, 30], 2), ([1000000000, 1, 1000000000, 2], 2)]
    for n in (30, 200):
        arr = [rng.randint(1, 15) for _ in range(n)]; T.append((arr, rng.randint(0, n)))
    arr = [rng.randint(1, 10 ** 9) for _ in range(100000)]; T.append((arr, 50000))
    arr = [rng.randint(1, 300) for _ in range(100000)]; T.append((arr, 70000))
    arr = [i // 3 + 1 for i in range(100000)]; T.append((arr, 99999))
    return [minids_in(a, m) for a, m in T]


def tests_twodenom():
    T = [([5], 1, [5, 10, 4]), ([1, 2], 3, [6, 7, 3, 1]), ([3, 7], 10, [1, 2, 10, 70, 71, 23]),
         ([2, 5, 11], 4, [44, 45, 9, 22, 13, 3, 27]),
         ([1, 10, 100, 1000], 20, [1, 99, 1999, 20000, 12345, 20001, 2200])]
    a = sorted(rng.sample(range(1, 200), 30)); T.append((a, 8, [rng.randint(1, 1500) for _ in range(20)]))
    a = sorted(rng.sample(range(1, 10 ** 7), 5000))
    qs = [rng.choice(a) * rng.randint(1, 12) + rng.choice(a) * rng.randint(0, 8) for _ in range(15)] + \
         [rng.randint(1, 2 * 10 ** 8) for _ in range(5)]
    T.append((a, 20, qs))
    a = list(range(9999000, 10000000)) + sorted(rng.sample(range(1, 9999000), 4000))
    T.append((sorted(a), 20, [2 * 10 ** 8, 199999999, 1, 9999000 * 20, rng.randint(1, 2 * 10 ** 8)] +
              [rng.randint(10 ** 7, 2 * 10 ** 8) for _ in range(15)]))
    return [twodenom_in(*t) for t in T]


def tests_majparts():
    T = [[1], [4, 4, 4, 9], [1, 2], [1, 2, 3, 4, 5, 6], [7, 7, 8, 8], [3, 3, 1, 2, 3, 4, 5, 6, 3],
         [5, 5, 5, 5, 6, 6, 6, 7, 8, 9, 10, 11, 12]]
    for n in (40, 300):
        T.append([rng.randint(1, rng.randint(2, 40)) for _ in range(n)])
    T.append([rng.randint(1, 10 ** 9) for _ in range(100000)])
    T.append([rng.randint(1, 1000) for _ in range(100000)])
    T.append([i % 50000 for i in range(100000)])
    T.append([1] * 49999 + list(range(2, 50003)))
    return [majparts_in(a) for a in T]


def tests_palsubs():
    T = [["a", "ab", "zzz", "abcd"], ["abcba", "aabbcc", "qwertyuiop"]]
    T.append(["".join(rng.choice("ab") for _ in range(rng.randint(1, 40))) for _ in range(6)])
    T.append(["".join(rng.choice("abcdefghij") for _ in range(rng.randint(1, 200))) for _ in range(50)])
    T.append(["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(1, 30))) for _ in range(1000)])
    T.append(["a" * 200000])
    T.append(["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(200000))])
    T.append(["".join(rng.choice("ab") for _ in range(100000)), "".join(rng.choice("xyz") for _ in range(100000))])
    return [palsubs_in(t) for t in T]


def tests_beauty():
    T = ["a", ".", "....", "abc", "a.b", "a..a", ".a.", "ab...ba", "a.b.c.d", "b..a.......c.a",
         "zz.z..y.yy...x"]
    for n in (25, 300):
        T.append("".join(rng.choice("abc....") for _ in range(n)))
    T.append("." * 200000)
    T.append("".join(rng.choice("ab" + "." * 6) for _ in range(200000)))
    T.append("".join(rng.choice("abcdefghijklmnopqrstuvwxyz.") for _ in range(200000)))
    T.append(("ab" + "." * 998) * 200)
    return [t + "\n" for t in T]


# ---------------------------------------------------------------- statements
Q = [
 {"id": "minids", "title": "Fewest IDs After Removals", "diff": "Easy",
  "src": SRC + " (Embedded Systems role, HackerRank). Coding question 1 of 2.",
  "body": "<p>You are given a list of IDs <code>arr</code> and an integer <code>m</code>. Remove <b>exactly</b> <code>m</code> elements from the list (any elements you like).</p><p>Return the <b>minimum number of distinct IDs</b> that can remain.</p>",
  "inp": "The first line contains <code>n</code> and <code>m</code>. The second line contains the <code>n</code> IDs.",
  "out": "One integer: the fewest distinct IDs left.",
  "cons": ["1 ≤ n ≤ 10<sup>5</sup>", "0 ≤ m ≤ n", "1 ≤ arr[i] ≤ 10<sup>9</sup>"],
  "samples": [{"in": "9 2\n1 3 1 4 1 1 1 2 2\n", "ex": "Remove the single 3 and the single 4. Only IDs 1 and 2 are left."},
              {"in": "6 3\n5 5 2 7 7 7\n", "ex": "Removing 2 (one element) and both 5s (two elements) leaves only 7."}],
  "py": MINIDS_PY, "cpp": MINIDS_CPP, "tests": tests_minids,
  "lc": "1481 Least Number of Unique Integers after K Removals",
  "lcurl": "https://leetcode.com/problems/least-number-of-unique-integers-after-k-removals/"},

 {"id": "twodenom", "title": "Fewest Notes, Two Denominations", "diff": "Medium",
  "src": SRC + " (Embedded Systems role, HackerRank). Coding question 2 of 2. The reported statement was garbled; the samples show the answer is the smallest a + b.",
  "body": "<p>You are given the values <code>arr</code> (think of them as banknote denominations, each available in unlimited supply), a list of amounts <code>query</code>, and an integer <code>k</code>.</p><p>For each amount <code>x</code>, find non-negative integers <code>a</code>, <code>b</code> and indices <code>i</code>, <code>j</code> with</p><p style=\"text-align:center\"><code>a · arr[i] + b · arr[j] = x</code> and <code>a + b ≤ k</code>,</p><p>so that <code>a + b</code> is as <b>small</b> as possible. In other words, pay <code>x</code> with at most <code>k</code> notes taken from at most two denominations, using as few notes as possible.</p><p>Output that smallest <code>a + b</code> for every query, or <code>-1</code> if the amount can't be paid.</p>",
  "inp": "Line 1: <code>n</code> and <code>k</code>. Line 2: the <code>n</code> values of <code>arr</code>. Line 3: <code>q</code>. Line 4: the <code>q</code> amounts.",
  "out": "<code>q</code> integers on one line, separated by spaces.",
  "cons": ["1 ≤ n ≤ 5000", "1 ≤ k ≤ 20", "1 ≤ arr[i] ≤ 10<sup>7</sup>", "1 ≤ q ≤ 20", "1 ≤ query[i] ≤ 2 × 10<sup>8</sup>"],
  "samples": [{"in": "5 5\n1 2 3 6 67\n5\n1 4 30 70 89\n", "ex": "1 = 1·1 (one note). 4 = 2·2 or 1 + 3 (two notes). 30 = 5·6 (five notes; four notes reach at most 24 without 67). 70 = 67 + 3 (two notes). 89 can't be paid with at most 5 notes from two denominations."},
              {"in": "2 4\n10 3\n4\n13 40 41 7\n", "ex": "13 = 10 + 3 (two notes). 40 = 4·10 (four notes). 41 = 2·10 + 7·3 needs nine notes, more than k = 4. 7 can't be made from 10s and 3s at all."}],
  "py": TWODENOM_PY, "cpp": TWODENOM_CPP, "tests": tests_twodenom,
  "lc": "322 Coin Change (related; Codeforces 529D / 524C is the exact problem)",
  "lcurl": "https://codeforces.com/problemset/problem/529/D"},

 {"id": "majparts", "title": "Fewest Subsequences With a Majority", "diff": "Medium",
  "src": SRC + " (Software Engineer role). Coding question 1 of 3.",
  "body": "<p>You are given an integer array <code>arr</code> of length <code>n</code>. Split it into subsequences so that every element belongs to exactly one subsequence, and every subsequence has a <b>majority element</b>: a value that occurs strictly more than half the subsequence's length.</p><p>Return the minimum number of subsequences needed.</p>",
  "inp": "The first line contains <code>n</code>. The second line contains the <code>n</code> elements.",
  "out": "One integer: the minimum number of subsequences.",
  "cons": ["1 ≤ n ≤ 10<sup>5</sup>", "1 ≤ arr[i] ≤ 10<sup>9</sup>"],
  "samples": [{"in": "6\n2 2 2 1 3 4\n", "ex": "2 appears 3 times, which is not more than 6 / 2, so one subsequence isn't enough. [2, 2, 2, 1, 3] has majority 2 (3 > 5/2), and [4] on its own is fine: 2 subsequences."},
              {"in": "4\n1 2 3 4\n", "ex": "Any subsequence with two different values has no majority, so every value needs its own subsequence: 4."}],
  "py": MAJPARTS_PY, "cpp": MAJPARTS_CPP, "tests": tests_majparts,
  "lc": "169 Majority Element (related)", "lcurl": "https://leetcode.com/problems/majority-element/"},

 {"id": "palsubs", "title": "Substrings That Rearrange Into Palindromes", "diff": "Medium",
  "src": SRC + " (Software Engineer role). Coding question 2 of 3.",
  "body": "<p>You are given several strings of lowercase letters. For each string, count its <b>substrings</b> (contiguous, non-empty, counted by position) whose letters can be rearranged to form a palindrome.</p><p>A multiset of letters can form a palindrome exactly when at most one letter occurs an odd number of times.</p>",
  "inp": "The first line contains <code>T</code>. Each of the next <code>T</code> lines contains one string.",
  "out": "<code>T</code> lines: the count for each string. Counts can exceed 2<sup>31</sup>.",
  "cons": ["1 ≤ T ≤ 10<sup>4</sup>", "Total length of all strings ≤ 2 × 10<sup>5</sup>", "Strings contain only <code>a</code>–<code>z</code>"],
  "samples": [{"in": "2\naba\nabc\n", "ex": "aba: a, b, a, aba (ab and ba have two odd letters): 4. abc: only the three single letters: 3."},
              {"in": "1\naabb\n", "ex": "The 4 single letters, aa and bb, aab and abb (one odd letter each), and aabb itself: 4 + 2 + 2 + 1 = 9. ab has two odd letters, so it doesn't count."}],
  "py": PALSUBS_PY, "cpp": PALSUBS_CPP, "tests": tests_palsubs,
  "lc": "1915 Number of Wonderful Substrings",
  "lcurl": "https://leetcode.com/problems/number-of-wonderful-substrings/"},

 {"id": "beauty", "title": "Fill the Dots for the Most Uniform Substrings", "diff": "Hard",
  "src": SRC + " (Software Engineer role). Coding question 3 of 3.",
  "body": "<p>You are given a string <code>s</code> of lowercase letters and dots (<code>.</code>). Replace every dot with any lowercase letter.</p><p>A substring is <b>beautiful</b> if all its characters are the same. Substrings are counted by position, so a block of <code>L</code> equal letters contains <code>L(L+1)/2</code> beautiful substrings.</p><p>Return the largest possible number of beautiful substrings after replacing the dots.</p>",
  "inp": "One line with the string <code>s</code>.",
  "out": "One integer: the maximum number of beautiful substrings. It can exceed 2<sup>31</sup>.",
  "cons": ["1 ≤ |s| ≤ 2 × 10<sup>5</sup>", "<code>s</code> contains only <code>a</code>–<code>z</code> and <code>.</code>"],
  "samples": [{"in": "a..b\n", "ex": "aaab gives blocks of 3 and 1: 6 + 1 = 7. aabb gives 3 + 3 = 6, so 7 is best."},
              {"in": "ab..a.b\n", "ex": "Turn every dot into a: abaaaab has blocks a, b, aaaa, b, giving 1 + 1 + 10 + 1 = 13. Extending the b blocks instead (e.g. abbbabb, 1 + 6 + 1 + 3 = 11) is worse."}],
  "py": BEAUTY_PY, "cpp": BEAUTY_CPP, "tests": tests_beauty,
  "lc": "1759 Count Number of Homogenous Substrings (related)",
  "lcurl": "https://leetcode.com/problems/count-number-of-homogenous-substrings/"},
]


def main():
    verify()
    os.makedirs(OUT, exist_ok=True)
    for q in Q:
        samples = [{"in": s["in"], "out": run_py(q["py"], s["in"]), "ex": s["ex"]} for s in q["samples"]]
        hidden = [{"in": t, "out": run_py(q["py"], t)} for t in q["tests"]()]
        doc = {"id": q["id"], "type": "code", "title": q["title"], "diff": q["diff"], "src": q["src"],
               "body": q["body"], "inp": q["inp"], "out": q["out"], "cons": q["cons"],
               "samples": samples, "hidden": hidden, "ref": q["py"], "refcpp": q["cpp"],
               "lc": q["lc"], "lcurl": q["lcurl"]}
        with open(os.path.join(OUT, q["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("wrote %-9s samples=%s  hidden=%d" % (q["id"], [s["out"] for s in samples], len(hidden)))


if __name__ == "__main__":
    main()
