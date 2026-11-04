# Amazon 2024 online coding OA (HackerRank)

Five coding questions reported from Amazon's 2024 online assessments on
HackerRank (test slug `rfe1p4jtmt`, FTE / online sittings, Aug–Sep 2024). Each
candidate was shown two coding questions drawn from this pool, so the "Question
1 / Question 2" labels on the originals vary between sittings.

Statements are paraphrased from candidates' screenshots. Where the original did
not show a constraint, a reasonable one is assumed and noted below. All five are
LeetCode-style (complete a function; a hidden driver does the I/O).

---

## 1. Pairs with sum divisible by X — `findPairs(x, cost)`

Amazon offers a discount on every purchase of a pair of products whose cost sum
is divisible by `x`. Given `n` product costs, count the pairs `(i, j)` with
`i < j` and `(cost[i] + cost[j]) % x == 0`.

- **Example:** `x = 60`, `cost = [31, 25, 85, 29, 35]` → `3` — the pairs
  `(31, 29)`, `(25, 35)`, `(85, 35)`.
- **Constraints (from the screenshot):** `1 ≤ x ≤ 2·10^9`, `1 ≤ n ≤ 10^5`,
  `1 ≤ cost[i] ≤ 10^9`.
- **Approach:** bucket costs by remainder mod `x`; a remainder `r` pairs with
  `(x − r) % x`. O(n). Same pattern as LeetCode 1010.
- **Note:** the original says the function returns `int`, but with `x = 1` the
  count is `n(n−1)/2 ≈ 5·10^9`, which overflows 32 bits, so a 64-bit return is
  used here.

## 2. Minimise the maximum load — `getMinMaxParcels(parcels, extra_parcels)`

`n` delivery agents start with `parcels[i]` parcels each; `extra_parcels` more
must all be assigned. Assign them so the maximum load on any agent is as small
as possible, and return that minimum possible maximum.

- **Example:** `parcels = [7, 5, 1, 9, 1]`, `extra = 25` → `10`.
- **Constraints:** `1 ≤ n ≤ 10^5`, `1 ≤ parcels[i] ≤ 10^9` (assumed);
  `extra_parcels` is a `LONG_INTEGER`, taken here as `0 ≤ extra ≤ 10^12`.
- **Approach:** binary-search the answer `L`; it is feasible when
  `Σ max(0, L − parcels[i]) ≥ extra`. O(n log).

## 3. Largest potential outlier — `getOutlierValue(arr)`

An array of `n` integers holds `n − 2` "normal" numbers, their sum (so `n − 1`
values), and one more value — the outlier — which is neither a normal number
nor their sum. Several values may qualify; return the greatest.

- **Example:** `arr = [4, 1, 3, 16, 2, 10]` → `16` (both 16 and 4 qualify).
- **Constraints:** `3 ≤ n ≤ 10^5` (assumed); values taken here as
  `−10^6 ≤ arr[i] ≤ 10^6`. A valid outlier is guaranteed to exist.
- **Approach:** let `S` be the total. A value `o` can be the outlier iff
  `S − o` is even and `(S − o)/2` is present at another index. Return the max
  such `o`. O(n). This is LeetCode 3371.

## 4. Capable tournament winners — `findCapableWinners(power_a, power_b, power_c)`

Each game has 3 rounds; every player holds exactly three power boosters, each
used at most once, and the higher booster wins a round. The `i`-th of `n`
players has boosters `(power_a[i], power_b[i], power_c[i])`. Player X is capable
of defeating player Y if, choosing booster orders, X can win at least 2 of the 3
rounds. Count the players capable of defeating every other player.

- **Example:** `power_a = [3, 4, 1, 16]`, `power_b = [2, 11, 5, 6]`,
  `power_c = [8, 7, 9, 10]` → `2` (the players holding `{4,11,7}` and
  `{16,6,10}`).
- **Constraints:** `2 ≤ n ≤ 10^5`, `1 ≤ power_*[i] ≤ 10^9`, each player's three
  boosters distinct.
- **Approach:** sort each player's triple to `(lo ≤ mid ≤ hi)`. X beats Y iff
  `X.mid > Y.lo` and `X.hi > Y.mid` (this is exactly "X can win ≥2 of 3"). So a
  player `i` is capable iff `mid[i] > max_{j≠i} lo[j]` and
  `hi[i] > max_{j≠i} mid[j]`; compute the two global top-2 maxima. O(n log n).

## 5. Fewest wildcards in a common pattern — `minQuestionMarks(patterns)`

A pattern is lowercase letters and `?` wildcards (each `?` matches any one
letter). Two patterns intersect if the wildcards can be filled so both yield the
same string. Given `n` equal-length patterns, find the minimum number of `?` a
pattern can have while still intersecting all of them.

- **Example:** `patterns = ["ha???rrank", "?a?ke?bank"]` → `1` (e.g.
  `hacker?ank`).
- **Constraints:** `1 ≤ n ≤ 10^4`, all patterns share one length
  `1 ≤ m ≤ 10^3` (assumed); lowercase letters and `?`.
- **Approach:** per column, a single fixed letter works unless two patterns pin
  two *different* letters there; such a column forces one `?`. The answer is the
  number of columns with ≥2 distinct non-`?` letters. O(n·m).
- **Assumption:** the screenshot did not show the custom-input format or whether
  patterns can differ in length; equal length is assumed (otherwise "intersect"
  is ill-defined).
