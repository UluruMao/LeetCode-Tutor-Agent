##  Max Consecutive Ones III
**Date:** 2026-04-07 01:13
**Status/Error:** `Wrong Answer`

### The Flaw & Hint
It looks like you've got a solid grasp on the sliding window pattern for this problem, which is a great start! Your approach of expanding the window with `right` and shrinking it with `left` when `curr` (the count of zeros) exceeds `k` is correct.

However, there's a small but crucial detail in how you're calculating the length of your valid window.

Let's trace your code with the provided test case: `nums = [1,1,1,0,0,0,1,1,1,1,0], k = 2`.
Your code returns `5`.

Consider a simple window, for example, `nums = [1,1,1]`.
If `left = 0` and `right = 2`, the actual length of this window is 3.
Your current calculation `right - left` would give `2 - 0 = 2`.

This difference in length calculation means your `ans` variable might not be capturing the true maximum length of the valid windows you identify.

How do you typically calculate the number of elements in a contiguous range given its starting and ending indices (inclusive)?

---

