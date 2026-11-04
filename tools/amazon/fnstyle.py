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
_JNEXT = r"""
    private static long nextLong(DataInputStream in) throws IOException {
        long r = 0; int b = in.read(); boolean neg = false;
        while (b != -1 && (b < '0' || b > '9') && b != '-') b = in.read();
        if (b == '-') { neg = true; b = in.read(); }
        while (b >= '0' && b <= '9') { r = r * 10 + (b - '0'); b = in.read(); }
        return neg ? -r : r;
    }"""

SPEC.update({
 # ---- Q: pairs whose cost sum is divisible by x ----
 "findpairs": {
  "name": "findPairs", "sig": "findPairs(x, cost)",
  "returns": "the number of pairs whose cost sum is divisible by x",
  "params": [("x", "the divisor"), ("cost", "the list of product costs")],
  "stub": {
   "py": "class Solution:\n    def findPairs(self, x: int, cost: List[int]) -> int:\n        pass\n",
   "cpp": "class Solution {\npublic:\n    long long findPairs(long long x, vector<int>& cost) {\n        \n        return 0;\n    }\n};\n",
   "java": "class Solution {\n    public long findPairs(long x, int[] cost) {\n        \n        return 0;\n    }\n}\n",
   "js": "/**\n * @param {number} x\n * @param {number[]} cost\n * @return {number}\n */\nvar findPairs = function(x, cost) {\n    \n};\n",
  },
  "post": {
   "py": r'''

if __name__ == "__main__":
    _d = sys.stdin.buffer.read().split()
    _x = int(_d[0]); _n = int(_d[1])
    _cost = list(map(int, _d[2:2 + _n]))
    print(Solution().findPairs(_x, _cost))
''',
   "cpp": r'''

int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    long long x; int n; cin >> x >> n;
    vector<int> cost(n);
    for (auto& v : cost) cin >> v;
    cout << Solution().findPairs(x, cost) << "\n";
    return 0;
}
''',
   "java": r'''

public class Main {
    public static void main(String[] args) throws IOException {
        DataInputStream in = new DataInputStream(new BufferedInputStream(System.in, 1 << 16));
        long x = nextLong(in); int n = (int) nextLong(in);
        int[] cost = new int[n];
        for (int i = 0; i < n; i++) cost[i] = (int) nextLong(in);
        System.out.println(new Solution().findPairs(x, cost));
    }''' + _JNEXT + '''
}
''',
   "js": r'''

;(() => {
    const _d = require("fs").readFileSync(0, "utf8").trim().split(/\s+/);
    const x = Number(_d[0]), n = Number(_d[1]);
    const cost = _d.slice(2, 2 + n).map(Number);
    console.log(String(findPairs(x, cost)));
})();
''',
  },
  "ref": {
   "py": r'''class Solution:
    def findPairs(self, x: int, cost: List[int]) -> int:
        c = Counter(v % x for v in cost)
        ans = 0
        for r, cnt in c.items():
            s = (x - r) % x
            if s == r:
                ans += cnt * (cnt - 1) // 2
            elif r < s:
                ans += cnt * c.get(s, 0)
        return ans
''',
   "cpp": r'''class Solution {
public:
    long long findPairs(long long x, vector<int>& cost) {
        unordered_map<long long, long long> c;
        for (int v : cost) c[v % x]++;
        long long ans = 0;
        for (auto& kv : c) {
            long long r = kv.first, cnt = kv.second, s = (x - r) % x;
            if (s == r) ans += cnt * (cnt - 1) / 2;
            else if (r < s) { auto it = c.find(s); if (it != c.end()) ans += cnt * it->second; }
        }
        return ans;
    }
};
''',
   "java": r'''class Solution {
    public long findPairs(long x, int[] cost) {
        HashMap<Long, Long> c = new HashMap<>();
        for (int v : cost) c.merge(v % x, 1L, Long::sum);
        long ans = 0;
        for (Map.Entry<Long, Long> e : c.entrySet()) {
            long r = e.getKey(), cnt = e.getValue(), s = (x - r) % x;
            if (s == r) ans += cnt * (cnt - 1) / 2;
            else if (r < s) { Long o = c.get(s); if (o != null) ans += cnt * o; }
        }
        return ans;
    }
}
''',
   "js": r'''var findPairs = function(x, cost) {
    const c = new Map();
    for (const v of cost) { const r = v % x; c.set(r, (c.get(r) || 0) + 1); }
    let ans = 0;
    for (const [r, cnt] of c) {
        const s = (x - r) % x;
        if (s === r) ans += cnt * (cnt - 1) / 2;
        else if (r < s) ans += cnt * (c.get(s) || 0);
    }
    return ans;
};
''',
  },
 },
 # ---- Q: minimise the maximum load ----
 "parcels": {
  "name": "getMinMaxParcels", "sig": "getMinMaxParcels(parcels, extraParcels)",
  "returns": "the minimum possible value of the maximum load",
  "params": [("parcels", "the initial parcels per agent"), ("extraParcels", "the extra parcels to assign")],
  "stub": {
   "py": "class Solution:\n    def getMinMaxParcels(self, parcels: List[int], extraParcels: int) -> int:\n        pass\n",
   "cpp": "class Solution {\npublic:\n    long long getMinMaxParcels(vector<int>& parcels, long long extraParcels) {\n        \n        return 0;\n    }\n};\n",
   "java": "class Solution {\n    public long getMinMaxParcels(int[] parcels, long extraParcels) {\n        \n        return 0;\n    }\n}\n",
   "js": "/**\n * @param {number[]} parcels\n * @param {number} extraParcels\n * @return {number}\n */\nvar getMinMaxParcels = function(parcels, extraParcels) {\n    \n};\n",
  },
  "post": {
   "py": r'''

if __name__ == "__main__":
    _d = sys.stdin.buffer.read().split()
    _n = int(_d[0])
    _parcels = list(map(int, _d[1:1 + _n]))
    _extra = int(_d[1 + _n])
    print(Solution().getMinMaxParcels(_parcels, _extra))
''',
   "cpp": r'''

int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<int> parcels(n);
    for (auto& p : parcels) cin >> p;
    long long extra; cin >> extra;
    cout << Solution().getMinMaxParcels(parcels, extra) << "\n";
    return 0;
}
''',
   "java": r'''

public class Main {
    public static void main(String[] args) throws IOException {
        DataInputStream in = new DataInputStream(new BufferedInputStream(System.in, 1 << 16));
        int n = (int) nextLong(in);
        int[] parcels = new int[n];
        for (int i = 0; i < n; i++) parcels[i] = (int) nextLong(in);
        long extra = nextLong(in);
        System.out.println(new Solution().getMinMaxParcels(parcels, extra));
    }''' + _JNEXT + '''
}
''',
   "js": r'''

;(() => {
    const _d = require("fs").readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
    const n = _d[0];
    const parcels = _d.slice(1, 1 + n);
    const extra = _d[1 + n];
    console.log(String(getMinMaxParcels(parcels, extra)));
})();
''',
  },
  "ref": {
   "py": r'''class Solution:
    def getMinMaxParcels(self, parcels: List[int], extraParcels: int) -> int:
        lo, hi = max(parcels), max(parcels) + extraParcels
        def room(L):
            s = 0
            for p in parcels:
                if p < L:
                    s += L - p
                    if s >= extraParcels:
                        return s
            return s
        while lo < hi:
            mid = (lo + hi) // 2
            if room(mid) >= extraParcels:
                hi = mid
            else:
                lo = mid + 1
        return lo
''',
   "cpp": r'''class Solution {
public:
    long long getMinMaxParcels(vector<int>& parcels, long long extraParcels) {
        long long lo = 0;
        for (int p : parcels) lo = max(lo, (long long) p);
        long long hi = lo + extraParcels;
        auto room = [&](long long L) -> long long {
            long long s = 0;
            for (int p : parcels) if (p < L) { s += L - p; if (s >= extraParcels) return s; }
            return s;
        };
        while (lo < hi) {
            long long mid = lo + (hi - lo) / 2;
            if (room(mid) >= extraParcels) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
};
''',
   "java": r'''class Solution {
    public long getMinMaxParcels(int[] parcels, long extraParcels) {
        long lo = 0;
        for (int p : parcels) lo = Math.max(lo, (long) p);
        long hi = lo + extraParcels;
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2;
            long s = 0;
            for (int p : parcels) if (p < mid) { s += mid - p; if (s >= extraParcels) break; }
            if (s >= extraParcels) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
}
''',
   "js": r'''var getMinMaxParcels = function(parcels, extraParcels) {
    let lo = 0;
    for (const p of parcels) if (p > lo) lo = p;
    let hi = lo + extraParcels;
    const room = (L) => {
        let s = 0;
        for (const p of parcels) if (p < L) { s += L - p; if (s >= extraParcels) return s; }
        return s;
    };
    while (lo < hi) {
        const mid = Math.floor((lo + hi) / 2);
        if (room(mid) >= extraParcels) hi = mid; else lo = mid + 1;
    }
    return lo;
};
''',
  },
 },
 # ---- Q: largest potential outlier ----
 "outlier": {
  "name": "getOutlierValue", "sig": "getOutlierValue(arr)",
  "returns": "the greatest value that can be the outlier",
  "params": [("arr", "the array of integers")],
  "stub": {
   "py": "class Solution:\n    def getOutlierValue(self, arr: List[int]) -> int:\n        pass\n",
   "cpp": "class Solution {\npublic:\n    int getOutlierValue(vector<int>& arr) {\n        \n        return 0;\n    }\n};\n",
   "java": "class Solution {\n    public int getOutlierValue(int[] arr) {\n        \n        return 0;\n    }\n}\n",
   "js": "/**\n * @param {number[]} arr\n * @return {number}\n */\nvar getOutlierValue = function(arr) {\n    \n};\n",
  },
  "post": {
   "py": r'''

if __name__ == "__main__":
    _d = sys.stdin.buffer.read().split()
    _n = int(_d[0])
    _arr = list(map(int, _d[1:1 + _n]))
    print(Solution().getOutlierValue(_arr))
''',
   "cpp": r'''

int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<int> arr(n);
    for (auto& v : arr) cin >> v;
    cout << Solution().getOutlierValue(arr) << "\n";
    return 0;
}
''',
   "java": r'''

public class Main {
    public static void main(String[] args) throws IOException {
        DataInputStream in = new DataInputStream(new BufferedInputStream(System.in, 1 << 16));
        int n = (int) nextLong(in);
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = (int) nextLong(in);
        System.out.println(new Solution().getOutlierValue(arr));
    }''' + _JNEXT + '''
}
''',
   "js": r'''

;(() => {
    const _d = require("fs").readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
    const n = _d[0];
    const arr = _d.slice(1, 1 + n);
    console.log(String(getOutlierValue(arr)));
})();
''',
  },
  "ref": {
   "py": r'''class Solution:
    def getOutlierValue(self, arr: List[int]) -> int:
        S = sum(arr)
        freq = Counter(arr)
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
''',
   "cpp": r'''class Solution {
public:
    int getOutlierValue(vector<int>& arr) {
        long long S = 0;
        unordered_map<long long, int> freq;
        for (int v : arr) { S += v; freq[v]++; }
        long long best = LLONG_MIN;
        for (int v : arr) {
            long long o = v, t = S - o;
            if (t % 2 != 0) continue;
            long long m = t / 2;
            auto it = freq.find(m);
            bool ok = (m == o) ? (it != freq.end() && it->second >= 2) : (it != freq.end());
            if (ok && o > best) best = o;
        }
        return (int) best;
    }
};
''',
   "java": r'''class Solution {
    public int getOutlierValue(int[] arr) {
        long S = 0;
        HashMap<Long, Integer> freq = new HashMap<>();
        for (int v : arr) { S += v; freq.merge((long) v, 1, Integer::sum); }
        long best = Long.MIN_VALUE;
        for (int v : arr) {
            long o = v, t = S - o;
            if (t % 2 != 0) continue;
            long m = t / 2;
            Integer f = freq.get(m);
            boolean ok = (m == o) ? (f != null && f >= 2) : (f != null);
            if (ok && o > best) best = o;
        }
        return (int) best;
    }
}
''',
   "js": r'''var getOutlierValue = function(arr) {
    let S = 0; const freq = new Map();
    for (const v of arr) { S += v; freq.set(v, (freq.get(v) || 0) + 1); }
    let best = -Infinity;
    for (const v of arr) {
        const o = v, t = S - o;
        if (t % 2 !== 0) continue;
        const m = t / 2;
        const f = freq.get(m) || 0;
        const ok = (m === o) ? f >= 2 : f >= 1;
        if (ok && o > best) best = o;
    }
    return best;
};
''',
  },
 },
 # ---- Q: capable tournament winners ----
 "winners": {
  "name": "findCapableWinners", "sig": "findCapableWinners(power_a, power_b, power_c)",
  "returns": "the number of players capable of defeating every other player",
  "params": [("power_a", "first booster of each player"), ("power_b", "second booster of each player"),
             ("power_c", "third booster of each player")],
  "stub": {
   "py": "class Solution:\n    def findCapableWinners(self, power_a: List[int], power_b: List[int], power_c: List[int]) -> int:\n        pass\n",
   "cpp": "class Solution {\npublic:\n    int findCapableWinners(vector<int>& power_a, vector<int>& power_b, vector<int>& power_c) {\n        \n        return 0;\n    }\n};\n",
   "java": "class Solution {\n    public int findCapableWinners(int[] power_a, int[] power_b, int[] power_c) {\n        \n        return 0;\n    }\n}\n",
   "js": "/**\n * @param {number[]} power_a\n * @param {number[]} power_b\n * @param {number[]} power_c\n * @return {number}\n */\nvar findCapableWinners = function(power_a, power_b, power_c) {\n    \n};\n",
  },
  "post": {
   "py": r'''

if __name__ == "__main__":
    _d = sys.stdin.buffer.read().split()
    _i = 0
    _n = int(_d[_i]); _i += 1
    _a = list(map(int, _d[_i:_i + _n])); _i += _n + 1
    _b = list(map(int, _d[_i:_i + _n])); _i += _n + 1
    _c = list(map(int, _d[_i:_i + _n]))
    print(Solution().findCapableWinners(_a, _b, _c))
''',
   "cpp": r'''

int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<int> a(n); for (auto& v : a) cin >> v;
    int nb; cin >> nb; vector<int> b(nb); for (auto& v : b) cin >> v;
    int nc; cin >> nc; vector<int> c(nc); for (auto& v : c) cin >> v;
    cout << Solution().findCapableWinners(a, b, c) << "\n";
    return 0;
}
''',
   "java": r'''

public class Main {
    public static void main(String[] args) throws IOException {
        DataInputStream in = new DataInputStream(new BufferedInputStream(System.in, 1 << 16));
        int n = (int) nextLong(in);
        int[] a = new int[n]; for (int i = 0; i < n; i++) a[i] = (int) nextLong(in);
        int nb = (int) nextLong(in);
        int[] b = new int[nb]; for (int i = 0; i < nb; i++) b[i] = (int) nextLong(in);
        int nc = (int) nextLong(in);
        int[] c = new int[nc]; for (int i = 0; i < nc; i++) c[i] = (int) nextLong(in);
        System.out.println(new Solution().findCapableWinners(a, b, c));
    }''' + _JNEXT + '''
}
''',
   "js": r'''

;(() => {
    const _d = require("fs").readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
    let _i = 0;
    const n = _d[_i++];
    const a = _d.slice(_i, _i + n); _i += n + 1;
    const b = _d.slice(_i, _i + n); _i += n + 1;
    const c = _d.slice(_i, _i + n);
    console.log(String(findCapableWinners(a, b, c)));
})();
''',
  },
  "ref": {
   "py": r'''class Solution:
    def findCapableWinners(self, power_a: List[int], power_b: List[int], power_c: List[int]) -> int:
        n = len(power_a)
        lo = [0] * n; mid = [0] * n; hi = [0] * n
        for i in range(n):
            lo[i], mid[i], hi[i] = sorted((power_a[i], power_b[i], power_c[i]))
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
        for i in range(n):
            max_lo = lo[l2] if i == l1 else lo[l1]
            max_mid = mid[m2] if i == m1 else mid[m1]
            if mid[i] > max_lo and hi[i] > max_mid:
                cnt += 1
        return cnt
''',
   "cpp": r'''class Solution {
public:
    int findCapableWinners(vector<int>& power_a, vector<int>& power_b, vector<int>& power_c) {
        int n = power_a.size();
        vector<int> lo(n), mid(n), hi(n);
        for (int i = 0; i < n; i++) {
            int x = power_a[i], y = power_b[i], z = power_c[i];
            if (x > y) swap(x, y);
            if (y > z) swap(y, z);
            if (x > y) swap(x, y);
            lo[i] = x; mid[i] = y; hi[i] = z;
        }
        auto top2 = [](const vector<int>& v) {
            int i1 = -1, i2 = -1;
            for (int i = 0; i < (int) v.size(); i++) {
                if (i1 < 0 || v[i] > v[i1]) { i2 = i1; i1 = i; }
                else if (i2 < 0 || v[i] > v[i2]) { i2 = i; }
            }
            return make_pair(i1, i2);
        };
        pair<int, int> lp = top2(lo), mp = top2(mid);
        int cnt = 0;
        for (int i = 0; i < n; i++) {
            int maxLo = (i == lp.first) ? lo[lp.second] : lo[lp.first];
            int maxMid = (i == mp.first) ? mid[mp.second] : mid[mp.first];
            if (mid[i] > maxLo && hi[i] > maxMid) cnt++;
        }
        return cnt;
    }
};
''',
   "java": r'''class Solution {
    public int findCapableWinners(int[] power_a, int[] power_b, int[] power_c) {
        int n = power_a.length;
        int[] lo = new int[n], mid = new int[n], hi = new int[n];
        for (int i = 0; i < n; i++) {
            int x = power_a[i], y = power_b[i], z = power_c[i];
            if (x > y) { int t = x; x = y; y = t; }
            if (y > z) { int t = y; y = z; z = t; }
            if (x > y) { int t = x; x = y; y = t; }
            lo[i] = x; mid[i] = y; hi[i] = z;
        }
        int[] lp = top2(lo), mp = top2(mid);
        int cnt = 0;
        for (int i = 0; i < n; i++) {
            int maxLo = (i == lp[0]) ? lo[lp[1]] : lo[lp[0]];
            int maxMid = (i == mp[0]) ? mid[mp[1]] : mid[mp[0]];
            if (mid[i] > maxLo && hi[i] > maxMid) cnt++;
        }
        return cnt;
    }
    private int[] top2(int[] v) {
        int i1 = -1, i2 = -1;
        for (int i = 0; i < v.length; i++) {
            if (i1 < 0 || v[i] > v[i1]) { i2 = i1; i1 = i; }
            else if (i2 < 0 || v[i] > v[i2]) { i2 = i; }
        }
        return new int[]{i1, i2};
    }
}
''',
   "js": r'''var findCapableWinners = function(power_a, power_b, power_c) {
    const n = power_a.length;
    const lo = new Array(n), mid = new Array(n), hi = new Array(n);
    for (let i = 0; i < n; i++) {
        const t = [power_a[i], power_b[i], power_c[i]].sort((p, q) => p - q);
        lo[i] = t[0]; mid[i] = t[1]; hi[i] = t[2];
    }
    const top2 = (v) => {
        let i1 = -1, i2 = -1;
        for (let i = 0; i < v.length; i++) {
            if (i1 < 0 || v[i] > v[i1]) { i2 = i1; i1 = i; }
            else if (i2 < 0 || v[i] > v[i2]) { i2 = i; }
        }
        return [i1, i2];
    };
    const lp = top2(lo), mp = top2(mid);
    let cnt = 0;
    for (let i = 0; i < n; i++) {
        const maxLo = (i === lp[0]) ? lo[lp[1]] : lo[lp[0]];
        const maxMid = (i === mp[0]) ? mid[mp[1]] : mid[mp[0]];
        if (mid[i] > maxLo && hi[i] > maxMid) cnt++;
    }
    return cnt;
};
''',
  },
 },
 # ---- Q: fewest '?' in a common pattern ----
 "qmarks": {
  "name": "minQuestionMarks", "sig": "minQuestionMarks(patterns)",
  "returns": "the fewest '?' in a pattern that intersects all of them",
  "params": [("patterns", "the patterns, all of the same length")],
  "stub": {
   "py": "class Solution:\n    def minQuestionMarks(self, patterns: List[str]) -> int:\n        pass\n",
   "cpp": "class Solution {\npublic:\n    int minQuestionMarks(vector<string>& patterns) {\n        \n        return 0;\n    }\n};\n",
   "java": "class Solution {\n    public int minQuestionMarks(String[] patterns) {\n        \n        return 0;\n    }\n}\n",
   "js": "/**\n * @param {string[]} patterns\n * @return {number}\n */\nvar minQuestionMarks = function(patterns) {\n    \n};\n",
  },
  "post": {
   "py": r'''

if __name__ == "__main__":
    _d = sys.stdin.read().split()
    _n = int(_d[0])
    _patterns = _d[1:1 + _n]
    print(Solution().minQuestionMarks(_patterns))
''',
   "cpp": r'''

int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<string> patterns(n);
    for (auto& s : patterns) cin >> s;
    cout << Solution().minQuestionMarks(patterns) << "\n";
    return 0;
}
''',
   "java": r'''

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder(); String line;
        while ((line = br.readLine()) != null) sb.append(line).append('\n');
        StringTokenizer st = new StringTokenizer(sb.toString());
        int n = Integer.parseInt(st.nextToken());
        String[] patterns = new String[n];
        for (int i = 0; i < n; i++) patterns[i] = st.nextToken();
        System.out.println(new Solution().minQuestionMarks(patterns));
    }
}
''',
   "js": r'''

;(() => {
    const _d = require("fs").readFileSync(0, "utf8").trim().split(/\s+/);
    const n = Number(_d[0]);
    const patterns = _d.slice(1, 1 + n);
    console.log(String(minQuestionMarks(patterns)));
})();
''',
  },
  "ref": {
   "py": r'''class Solution:
    def minQuestionMarks(self, patterns: List[str]) -> int:
        m = len(patterns[0])
        cnt = 0
        for j in range(m):
            seen = ''
            for p in patterns:
                ch = p[j]
                if ch == '?':
                    continue
                if not seen:
                    seen = ch
                elif seen != ch:
                    cnt += 1
                    break
        return cnt
''',
   "cpp": r'''class Solution {
public:
    int minQuestionMarks(vector<string>& patterns) {
        if (patterns.empty()) return 0;
        int m = patterns[0].size(), cnt = 0;
        for (int j = 0; j < m; j++) {
            char seen = 0;
            for (size_t i = 0; i < patterns.size(); i++) {
                char ch = patterns[i][j];
                if (ch == '?') continue;
                if (seen == 0) seen = ch;
                else if (seen != ch) { cnt++; break; }
            }
        }
        return cnt;
    }
};
''',
   "java": r'''class Solution {
    public int minQuestionMarks(String[] patterns) {
        if (patterns.length == 0) return 0;
        int m = patterns[0].length(), cnt = 0;
        for (int j = 0; j < m; j++) {
            char seen = 0;
            for (String p : patterns) {
                char ch = p.charAt(j);
                if (ch == '?') continue;
                if (seen == 0) seen = ch;
                else if (seen != ch) { cnt++; break; }
            }
        }
        return cnt;
    }
}
''',
   "js": r'''var minQuestionMarks = function(patterns) {
    if (patterns.length === 0) return 0;
    const m = patterns[0].length;
    let cnt = 0;
    for (let j = 0; j < m; j++) {
        let seen = '';
        for (const p of patterns) {
            const ch = p[j];
            if (ch === '?') continue;
            if (seen === '') seen = ch;
            else if (seen !== ch) { cnt++; break; }
        }
    }
    return cnt;
};
''',
  },
 },
})

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
