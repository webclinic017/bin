package av_slidingwindow;

public class MaximumSumSubarraySizeK {
	
	public static int maximumSumSubarraySizeK(int[] arr, int k) {
		// k must be greater
        if (arr.length < k) {
           System.out.println("Invalid");
           return -1;
        }
      
        // Compute sum of first window of size k
        int res = 0;
        for (int i=0; i<k; i++) {
            res += arr[i];
        }
      
        // Compute sums of remaining windows by removing first element of previous
        // window and adding last element of current window.
        int curr_sum = res;
        for (int i=k; i< arr.length; i++) {
           curr_sum += arr[i] - arr[i-k];
           res = Math.max(res, curr_sum);
        }
      
        return res;
	}

}
