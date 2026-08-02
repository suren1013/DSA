# Notes — Two Sum

## Key idea

A hash map turns the "find the complement" lookup from O(n) into O(1), giving an
overall O(n) single-pass solution instead of the O(n²) brute-force double loop.

## Edge cases

- [x] Empty input
- [x] Single element
- [x] Negative / zero values
- [x] Large inputs (performance)

## Mistakes & lessons

- A two-pass approach also works, but a single pass avoids storing indices that
  would be overwritten and handles the "same element twice" case naturally.

## Follow-ups / variations

- Three Sum (two pointers after sorting).
- Two Sum II — input array is sorted (two pointers, O(1) space).
- Count pairs that sum to target.

## References

- https://leetcode.com/problems/two-sum/