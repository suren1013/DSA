/**
 * Problem: Two Sum
 * Topic:   arrays
 * Source:  LeetCode
 * Link:    https://leetcode.com/problems/two-sum/
 *
 * Description:
 *   Given an array of integers nums and an integer target, return the indices
 *   of the two numbers such that they add up to target. Each input has exactly
 *   one solution, and the same element may not be used twice.
 *
 * Approach:
 *   Single pass with a hash map. For each number, check if its complement
 *   (target - num) is already in the map; if so, return both indices.
 *   Otherwise store the current number's index in the map.
 *
 * Complexity:
 *   Time:  O(n)
 *   Space: O(n)
 */
public class TwoSum {

    public static void main(String[] args) {
        TwoSum solver = new TwoSum();
        int[] result = solver.twoSum(new int[]{2, 7, 11, 15}, 9);
        System.out.println("[" + result[0] + ", " + result[1] + "]"); // [0, 1]
    }

    public int[] twoSum(int[] nums, int target) {
        java.util.Map<Integer, Integer> seen = new java.util.HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (seen.containsKey(complement)) {
                return new int[]{seen.get(complement), i};
            }
            seen.put(nums[i], i);
        }
        throw new IllegalArgumentException("No two sum solution");
    }
}