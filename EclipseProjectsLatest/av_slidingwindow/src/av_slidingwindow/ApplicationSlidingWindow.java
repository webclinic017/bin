package av_slidingwindow;

public class ApplicationSlidingWindow {
	
	public static void main(String[] args) {
//		int[] arr = {1, 4, 2, 10, 2, 3, 1, 0, 20};
//		int k = 4;
//		// A Simple Solution is to generate all subarrays of size k, compute their sums and 
//		// finally return the maximum of all sums. The time complexity of this solution is O(n*k).
//		// Following is an efficient solution:
//		int maxSum = MaximumSumSubarraySizeK.maximumSumSubarraySizeK(arr, k);
//		System.out.println("maxSum: " + maxSum);
		
//		int[] arr = {-8, 2, 3, -6, 10};
//		int k = 2;
//		FirstNegativeIntegerInWindowSizeK.firstNegativeIntegerInWindowSizeK(arr, k);
		
////		String text = "forxxorfxdofr";
////		String word = "for";
//		String text = "aabaabaa";
//        String word = "aaba";
//        System.out.print(NumberOfOccurrencesOfAnagram.numberOfOccurrencesOfAnagram(text, word));
		
//		int[] arr = {1, 2, 3, 1, 4, 5, 2, 3, 6};
//		int k = 3;
		int arr[] = { 12, 1, 78, 90, 57, 89, 56 };
		int k = 3;
		int[] maxInSubarrays = MaximumInSubarraysOfSizeK.maximumInSubarraysOfSizeK(arr, k);
		printArray(maxInSubarrays);
	}

	public static void printArray(int[] arr) {
		for (int i = 0; i < arr.length; i++) {
			System.out.print(arr[i] + " ");
		}
		System.out.println();
	}

}
