import java.util.*;

public class Solution {

    public static void main(String[] args) {
        System.out.println("Count of 1 bits in 5: " + countOnes(5));
    }

    public static int countOnes(int n) {
        int count = 0;
        while (n != 0) {
            count += (n & 1);
            n >>>= 1;
        }
        return count;
    }

}