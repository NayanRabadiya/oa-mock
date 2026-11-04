"""Turn the Amazon coding questions into LeetCode-style function questions:
stub = what the editor shows, driver = hidden pre/post code that does I/O."""
import json

PY_PRE = "from typing import *\nimport sys, math, collections, heapq, bisect, itertools, functools\nfrom collections import *\n"
CPP_PRE = "#include <bits/stdc++.h>\nusing namespace std;\n"
JAVA_PRE = "import java.util.*;\nimport java.io.*;\n"

SPEC = {
 "flip": {
  "name": "maxConsecutiveOnes",
  "sig": "maxConsecutiveOnes(log, k)", "returns": "the longest run of 1s after the best flip",
  "params": [("log", "string of 0s and 1s"), ("k", "the length of the substring to flip")],
  "stub": {
   "py": "class Solution:\n    def maxConsecutiveOnes(self, log: str, k: int) -> int:\n        pass\n",
   "cpp": "class Solution {\npublic:\n    int maxConsecutiveOnes(string log, int k) {\n        \n        return 0;\n    }\n};\n",
   "java": "class Solution {\n    public int maxConsecutiveOnes(String log, int k) {\n        \n        return 0;\n    }\n}\n",
   "js": "/**\n * @param {string} log\n * @param {number} k\n * @return {number}\n */\nvar maxConsecutiveOnes = function(log, k) {\n    \n};\n",
  },
  "post": {
   "py": "\n\nif __name__ == \"__main__\":\n    _d = sys.stdin.read().split()\n    print(Solution().maxConsecutiveOnes(_d[0], int(_d[1])))\n",
   "cpp": "\n\nint main() {\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n    string log; int k; cin >> log >> k;\n    cout << Solution().maxConsecutiveOnes(log, k) << \"\\n\";\n    return 0;\n}\n",
   "java": "\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringBuilder sb = new StringBuilder(); String line;\n        while ((line = br.readLine()) != null) sb.append(line).append(' ');\n        String[] t = sb.toString().trim().split(\"\\\\s+\");\n        System.out.println(new Solution().maxConsecutiveOnes(t[0], Integer.parseInt(t[1])));\n    }\n}\n",
   "js": "\n\n;(() => { const _d = require(\"fs\").readFileSync(0, \"utf8\").trim().split(/\\s+/); console.log(String(maxConsecutiveOnes(_d[0], Number(_d[1])))); })();\n",
  },
  "ref": {
   "py": "class Solution:\n    def maxConsecutiveOnes(self, log: str, k: int) -> int:\n        n = len(log)\n        left = [0] * n   # 1s ending at i\n        right = [0] * n  # 1s starting at i\n        for i in range(n):\n            left[i] = (left[i-1] + 1 if i else 1) if log[i] == '1' else 0\n        for i in range(n - 1, -1, -1):\n            right[i] = (right[i+1] + 1 if i < n - 1 else 1) if log[i] == '1' else 0\n        best = 0\n        for i in range(n - k + 1):\n            a = left[i-1] if i else 0\n            b = right[i+k] if i + k < n else 0\n            best = max(best, a + k + b)\n        return best\n",
   "cpp": "class Solution {\npublic:\n    int maxConsecutiveOnes(string log, int k) {\n        int n = log.size();\n        vector<int> L(n), R(n);   // 1s ending at i / starting at i\n        for (int i = 0; i < n; i++) L[i] = log[i] == '1' ? (i ? L[i-1] : 0) + 1 : 0;\n        for (int i = n - 1; i >= 0; i--) R[i] = log[i] == '1' ? (i + 1 < n ? R[i+1] : 0) + 1 : 0;\n        int best = 0;\n        for (int i = 0; i + k <= n; i++)\n            best = max(best, (i ? L[i-1] : 0) + k + (i + k < n ? R[i+k] : 0));\n        return best;\n    }\n};\n",
   "java": "class Solution {\n    public int maxConsecutiveOnes(String log, int k) {\n        int n = log.length();\n        int[] L = new int[n], R = new int[n];\n        for (int i = 0; i < n; i++) L[i] = log.charAt(i) == '1' ? (i > 0 ? L[i-1] : 0) + 1 : 0;\n        for (int i = n - 1; i >= 0; i--) R[i] = log.charAt(i) == '1' ? (i + 1 < n ? R[i+1] : 0) + 1 : 0;\n        int best = 0;\n        for (int i = 0; i + k <= n; i++) best = Math.max(best, (i > 0 ? L[i-1] : 0) + k + (i + k < n ? R[i+k] : 0));\n        return best;\n    }\n}\n",
   "js": "var maxConsecutiveOnes = function(log, k) {\n    const n = log.length, L = new Array(n).fill(0), R = new Array(n).fill(0);\n    for (let i = 0; i < n; i++) L[i] = log[i] === '1' ? (i ? L[i-1] : 0) + 1 : 0;\n    for (let i = n - 1; i >= 0; i--) R[i] = log[i] === '1' ? (i + 1 < n ? R[i+1] : 0) + 1 : 0;\n    let best = 0;\n    for (let i = 0; i + k <= n; i++) best = Math.max(best, (i ? L[i-1] : 0) + k + (i + k < n ? R[i+k] : 0));\n    return best;\n};\n",
  },
 },
 "palsub": {
  "name": "countPalindromicSubsequences",
  "sig": "countPalindromicSubsequences(s)", "returns": "the count modulo 10<sup>9</sup> + 7",
  "params": [("s", "string of lowercase letters")],
  "stub": {
   "py": "class Solution:\n    def countPalindromicSubsequences(self, s: str) -> int:\n        pass\n",
   "cpp": "class Solution {\npublic:\n    int countPalindromicSubsequences(string s) {\n        \n        return 0;\n    }\n};\n",
   "java": "class Solution {\n    public int countPalindromicSubsequences(String s) {\n        \n        return 0;\n    }\n}\n",
   "js": "/**\n * @param {string} s\n * @return {number}\n */\nvar countPalindromicSubsequences = function(s) {\n    \n};\n",
  },
  "post": {
   "py": "\n\nif __name__ == \"__main__\":\n    print(Solution().countPalindromicSubsequences(sys.stdin.read().split()[0]))\n",
   "cpp": "\n\nint main() {\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n    string s; cin >> s;\n    cout << Solution().countPalindromicSubsequences(s) << \"\\n\";\n    return 0;\n}\n",
   "java": "\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine().trim();\n        System.out.println(new Solution().countPalindromicSubsequences(s));\n    }\n}\n",
   "js": "\n\n;(() => { const _s = require(\"fs\").readFileSync(0, \"utf8\").trim().split(/\\s+/)[0]; console.log(String(countPalindromicSubsequences(_s))); })();\n",
  },
  "ref": {
   "py": "class Solution:\n    def countPalindromicSubsequences(self, s: str) -> int:\n        MOD = 10**9 + 7\n        cnt = [0] * 26\n        for c in s: cnt[ord(c) - 97] += 1\n        # a letter that appears c > 0 times can be taken an even (or odd) number of times in 2^(c-1) ways\n        ev = [pow(2, c - 1, MOD) if c else 1 for c in cnt]\n        od = [pow(2, c - 1, MOD) if c else 0 for c in cnt]\n        pre = [1] * 27; suf = [1] * 27\n        for i in range(26): pre[i+1] = pre[i] * ev[i] % MOD\n        for i in range(25, -1, -1): suf[i] = suf[i+1] * ev[i] % MOD\n        ans = pre[26]                    # every letter even\n        for j in range(26):              # exactly letter j odd\n            ans = (ans + od[j] * pre[j] % MOD * suf[j+1]) % MOD\n        return ans\n",
   "cpp": "class Solution {\npublic:\n    int countPalindromicSubsequences(string s) {\n        const long long MOD = 1e9 + 7;\n        long long cnt[26] = {0};\n        for (char c : s) cnt[c - 'a']++;\n        vector<long long> p2(s.size() + 1, 1);\n        for (size_t i = 1; i <= s.size(); i++) p2[i] = p2[i-1] * 2 % MOD;\n        long long ev[26], od[26], pre[27], suf[27];\n        for (int i = 0; i < 26; i++) { ev[i] = cnt[i] ? p2[cnt[i]-1] : 1; od[i] = cnt[i] ? p2[cnt[i]-1] : 0; }\n        pre[0] = 1; suf[26] = 1;\n        for (int i = 0; i < 26; i++) pre[i+1] = pre[i] * ev[i] % MOD;\n        for (int i = 25; i >= 0; i--) suf[i] = suf[i+1] * ev[i] % MOD;\n        long long ans = pre[26];\n        for (int j = 0; j < 26; j++) ans = (ans + od[j] * pre[j] % MOD * suf[j+1]) % MOD;\n        return (int)ans;\n    }\n};\n",
   "java": "class Solution {\n    public int countPalindromicSubsequences(String s) {\n        final long MOD = 1_000_000_007L;\n        long[] cnt = new long[26];\n        for (char c : s.toCharArray()) cnt[c - 'a']++;\n        long[] p2 = new long[s.length() + 1]; p2[0] = 1;\n        for (int i = 1; i <= s.length(); i++) p2[i] = p2[i-1] * 2 % MOD;\n        long[] ev = new long[26], od = new long[26], pre = new long[27], suf = new long[27];\n        for (int i = 0; i < 26; i++) { ev[i] = cnt[i] > 0 ? p2[(int)cnt[i]-1] : 1; od[i] = cnt[i] > 0 ? p2[(int)cnt[i]-1] : 0; }\n        pre[0] = 1; suf[26] = 1;\n        for (int i = 0; i < 26; i++) pre[i+1] = pre[i] * ev[i] % MOD;\n        for (int i = 25; i >= 0; i--) suf[i] = suf[i+1] * ev[i] % MOD;\n        long ans = pre[26];\n        for (int j = 0; j < 26; j++) ans = (ans + od[j] * pre[j] % MOD * suf[j+1]) % MOD;\n        return (int) ans;\n    }\n}\n",
   "js": "var countPalindromicSubsequences = function(s) {\n    const MOD = 1000000007n, cnt = new Array(26).fill(0);\n    for (const c of s) cnt[c.charCodeAt(0) - 97]++;\n    const p2 = [1n];\n    for (let i = 1; i <= s.length; i++) p2.push(p2[i-1] * 2n % MOD);\n    const ev = cnt.map(c => c ? p2[c-1] : 1n), od = cnt.map(c => c ? p2[c-1] : 0n);\n    const pre = [1n], suf = new Array(27).fill(1n);\n    for (let i = 0; i < 26; i++) pre.push(pre[i] * ev[i] % MOD);\n    for (let i = 25; i >= 0; i--) suf[i] = suf[i+1] * ev[i] % MOD;\n    let ans = pre[26];\n    for (let j = 0; j < 26; j++) ans = (ans + od[j] * pre[j] % MOD * suf[j+1]) % MOD;\n    return Number(ans);\n};\n",
  },
 },
 "evenrun": {
  "name": "countArrangements",
  "sig": "countArrangements(A)", "returns": "the number of valid rearrangements modulo 10<sup>9</sup> + 7",
  "params": [("A", "array of n distinct positive integers")],
  "stub": {
   "py": "class Solution:\n    def countArrangements(self, A: List[int]) -> int:\n        pass\n",
   "cpp": "class Solution {\npublic:\n    int countArrangements(vector<int>& A) {\n        \n        return 0;\n    }\n};\n",
   "java": "class Solution {\n    public int countArrangements(int[] A) {\n        \n        return 0;\n    }\n}\n",
   "js": "/**\n * @param {number[]} A\n * @return {number}\n */\nvar countArrangements = function(A) {\n    \n};\n",
  },
  "post": {
   "py": "\n\nif __name__ == \"__main__\":\n    _d = sys.stdin.buffer.read().split()\n    _n = int(_d[0])\n    print(Solution().countArrangements(list(map(int, _d[1:1 + _n]))))\n",
   "cpp": "\n\nint main() {\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n    int n; cin >> n;\n    vector<int> A(n);\n    for (auto& x : A) cin >> x;\n    cout << Solution().countArrangements(A) << \"\\n\";\n    return 0;\n}\n",
   "java": "\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        DataInputStream in = new DataInputStream(new BufferedInputStream(System.in, 1 << 16));\n        int n = nextInt(in);\n        int[] A = new int[n];\n        for (int i = 0; i < n; i++) A[i] = nextInt(in);\n        System.out.println(new Solution().countArrangements(A));\n    }\n    private static int nextInt(DataInputStream in) throws IOException {\n        int r = 0, b = in.read();\n        while (b < '0' || b > '9') { if (b == '-') { b = in.read(); int v = 0; while (b >= '0' && b <= '9') { v = v * 10 + (b - '0'); b = in.read(); } return -v; } b = in.read(); }\n        while (b >= '0' && b <= '9') { r = r * 10 + (b - '0'); b = in.read(); }\n        return r;\n    }\n}\n",
   "js": "\n\n;(() => { const _d = require(\"fs\").readFileSync(0, \"utf8\").trim().split(/\\s+/).map(Number); console.log(String(countArrangements(_d.slice(1, 1 + _d[0])))); })();\n",
  },
  "ref": {
   "py": "class Solution:\n    def countArrangements(self, A: List[int]) -> int:\n        MOD = 10**9 + 7\n        n = len(A)\n        e = sum(1 for x in A if x % 2 == 0); o = n - e\n        g = o + 1                       # gaps around the odd numbers\n        f = [1] * (n + 2)\n        for i in range(1, n + 2): f[i] = f[i-1] * i % MOD\n        inv = [1] * (n + 2)\n        inv[n+1] = pow(f[n+1], MOD - 2, MOD)\n        for i in range(n + 1, 0, -1): inv[i-1] = inv[i] * i % MOD\n        C = lambda x, y: 0 if y < 0 or y > x else f[x] * inv[y] % MOD * inv[x-y] % MOD\n        w = 0\n        for t in range(e // 2 + 1):     # t gaps hold 2 evens, e - 2t gaps hold 1\n            ones = e - 2 * t\n            if t + ones <= g:\n                w = (w + C(g, t) * C(g - t, ones)) % MOD\n        return f[o] * f[e] % MOD * w % MOD\n",
   "cpp": "class Solution {\n    static constexpr long long MOD = 1e9 + 7;\n    long long pw(long long b, long long e) { long long r = 1; b %= MOD; while (e) { if (e & 1) r = r * b % MOD; b = b * b % MOD; e >>= 1; } return r; }\npublic:\n    int countArrangements(vector<int>& A) {\n        int n = A.size(), e = 0;\n        for (int x : A) if (x % 2 == 0) e++;\n        int o = n - e, g = o + 1;               // gaps around the odd numbers\n        vector<long long> f(n + 2, 1), inv(n + 2, 1);\n        for (int i = 1; i <= n + 1; i++) f[i] = f[i-1] * i % MOD;\n        inv[n+1] = pw(f[n+1], MOD - 2);\n        for (int i = n + 1; i > 0; i--) inv[i-1] = inv[i] * i % MOD;\n        auto C = [&](int x, int y) -> long long { return (y < 0 || y > x) ? 0 : f[x] * inv[y] % MOD * inv[x-y] % MOD; };\n        long long w = 0;\n        for (int t = 0; 2 * t <= e; t++) {      // t gaps hold 2 evens, e - 2t gaps hold 1\n            int ones = e - 2 * t;\n            if (t + ones <= g) w = (w + C(g, t) * C(g - t, ones)) % MOD;\n        }\n        return (int)(f[o] * f[e] % MOD * w % MOD);\n    }\n};\n",
   "java": "class Solution {\n    static final long MOD = 1_000_000_007L;\n    long pw(long b, long e) { long r = 1; b %= MOD; while (e > 0) { if ((e & 1) == 1) r = r * b % MOD; b = b * b % MOD; e >>= 1; } return r; }\n    public int countArrangements(int[] A) {\n        int n = A.length, e = 0;\n        for (int x : A) if (x % 2 == 0) e++;\n        int o = n - e, g = o + 1;\n        long[] f = new long[n + 2], inv = new long[n + 2];\n        f[0] = 1; for (int i = 1; i <= n + 1; i++) f[i] = f[i-1] * i % MOD;\n        inv[n+1] = pw(f[n+1], MOD - 2);\n        for (int i = n + 1; i > 0; i--) inv[i-1] = inv[i] * i % MOD;\n        long w = 0;\n        for (int t = 0; 2 * t <= e; t++) {\n            int ones = e - 2 * t;\n            if (t + ones <= g) w = (w + C(f, inv, g, t) * C(f, inv, g - t, ones)) % MOD;\n        }\n        return (int) (f[o] * f[e] % MOD * w % MOD);\n    }\n    long C(long[] f, long[] inv, int x, int y) { return (y < 0 || y > x) ? 0 : f[x] * inv[y] % MOD * inv[x-y] % MOD; }\n}\n",
   "js": "var countArrangements = function(A) {\n    const MOD = 1000000007n, n = A.length;\n    let e = 0; for (const x of A) if (x % 2 === 0) e++;\n    const o = n - e, g = o + 1;\n    const f = [1n]; for (let i = 1; i <= n + 1; i++) f.push(f[i-1] * BigInt(i) % MOD);\n    const pw = (b, x) => { let r = 1n; b %= MOD; while (x > 0n) { if (x & 1n) r = r * b % MOD; b = b * b % MOD; x >>= 1n; } return r; };\n    const inv = new Array(n + 2); inv[n+1] = pw(f[n+1], MOD - 2n);\n    for (let i = n + 1; i > 0; i--) inv[i-1] = inv[i] * BigInt(i) % MOD;\n    const C = (x, y) => (y < 0 || y > x) ? 0n : f[x] * inv[y] % MOD * inv[x-y] % MOD;\n    let w = 0n;\n    for (let t = 0; 2 * t <= e; t++) { const ones = e - 2 * t; if (t + ones <= g) w = (w + C(g, t) * C(g - t, ones)) % MOD; }\n    return Number(f[o] * f[e] % MOD * w % MOD);\n};\n",
  },
 },
}
PRE = {"py": PY_PRE, "cpp": CPP_PRE, "java": JAVA_PRE, "js": ""}

def apply(qs):
    for q in qs:
        sp = SPEC.get(q["id"])
        if not sp: continue
        q["stub"] = sp["stub"]
        q["body"] = q["body"].replace("Print the maximum number", "Return the maximum number").replace("Print the count modulo", "Return the count modulo")
        q["out"] = "The value your function returns (the driver prints it): " + q["out"][0].lower() + q["out"][1:]
        q["driver"] = {l: {"pre": PRE[l], "post": sp["post"][l]} for l in PRE}
        q["ref"] = sp["ref"]["py"]; q["refcpp"] = sp["ref"]["cpp"]
        params = "".join("<li><code>%s</code>: %s</li>" % p for p in sp["params"])
        q["body"] += ("<h3>Function to complete</h3><p>Complete <code>%s</code>. It returns %s.</p><ul>%s</ul>"
                      "<p class=\"muted\">Input reading and printing are handled for you, like on LeetCode. The input format below is what the tests and <i>Custom input</i> use.</p>") % (sp["sig"], sp["returns"], params)
        if q["id"] in ("palsub", "evenrun"):
            q["body"] += "<p class=\"muted\">JavaScript: products of two values below 10<sup>9</sup> + 7 overflow a double, so use <code>BigInt</code> for the modular arithmetic.</p>"
    return qs
