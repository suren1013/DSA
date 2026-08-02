# Two Sum

- **Topic:** arrays
- **Difficulty:** easy
- **Source:** LeetCode — https://leetcode.com/problems/two-sum/

## Problem statement

Given an array of integers `nums` and an integer `target`, return the indices of
the two numbers such that they add up to `target`. Each input has exactly one
solution, and the same element may not be used twice. The answer can be returned
in any order.

## Examples

```
Input:  nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
```

## Approach

Single pass with a hash map. For each number, check if its complement
(`target - num`) is already in the map; if so, return both indices. Otherwise
store the current number's index in the map.

## Complexity

- **Time:** O(n)
- **Space:** O(n)