import java.util.*;

public class Solution {

    public static void main(String[] args) {
        int[] nums = {1, 2, 3, 4, 5};
        System.out.println("Sum: " + sum(nums));
    }

    public static int sum(int[] nums) {
        int total = 0;
        for (int n : nums) {
            total += n;
        }
        return total;
    }

}