package av_slidingwindow;

public class ApplicationSlidingWindow {
	
	public static void main(String[] args) {
//		int[] arr = {1, 4, 2, 10, 2, 3, 1, 0, 20};
//		int k = 4;
//		// A Simple Solution is to generate all subarrays of size k, compute their sums and 
//		// finally return the maximum of all sums. The time complexity of this solution is O(n*k).
//		// Following is an efficient solution:
//		int maxSum = MaximumSumSubarraySizeK.maximumSumSubarraySizeK(arr, k);
////		int maxSum = MaximumSumSubarraySizeK.maximumSumSubarraySizeKAV(arr, k);
//		System.out.println("maxSum: " + maxSum);
		
//		int[] arr = {-8, 2, 3, -6, 10};
//		int k = 2;
//		FirstNegativeIntegerInWindowSizeK.firstNegativeIntegerInWindowSizeK(arr, k);
		
////		String text = "forxxorfxdofr";
////		String word = "for";
//		String text = "aabaabaa";
//        String word = "aaba";
//        System.out.print(NumberOfOccurrencesOfAnagram.numberOfOccurrencesOfAnagram(text, word));
		
////		int[] arr = {1, 2, 3, 1, 4, 5, 2, 3, 6};
////		int k = 3;
//		int arr[] = { 12, 1, 78, 90, 57, 89, 56 };
//		int k = 3;
//		int[] maxInSubarrays = MaximumInSubarraysOfSizeK.maximumInSubarraysOfSizeK(arr, k);
//		printArray(maxInSubarrays);
		
////		int[] arr = { 10, 5, 2, 7, 1, 9 };
////		int k = 15;
//		int[] arr = { -5, 8, -14, 2, 4, 12 };
//		int k = -5;
//		int sizeOfSubarray = LongestSubarrayOfSumK.longestSubarrayOfSumK(arr, k);
//		System.out.println("sizeOfSubarray : " + sizeOfSubarray);
		
//		String s = "aabbcc";
//		int k = 3;
//		// If the length of string is n, then there can be n*(n+1)/2 possible substrings. A simple way 
//		// is to generate all the substring and check each one whether it has exactly k unique characters 
//		// or not. If we apply this brute force, it would take O(n2) to generate all substrings and O(n) 
//		// to do a check on each one. Thus overall it would go O(n3). To generate all the substrings, run
//		// two for loops with i, j from 0 to arr.length.
//		// We can further improve this solution by creating a hash table and while generating the substrings, 
//		// check the number of unique characters using that hash table. Thus it would improve up to O(n2).
//		String subString = LongestSubstringWithKUniqueCharacters.longestSubstringWithKUniqueCharacters(s, k);
//		System.out.println("subString: " + subString);
		
//		String str = "aabbcc";
//		// Approach 1: We can consider all substrings one by one and check for each substring whether it
//		// contains all unique characters or not. There will be n*(n+1)/2 substrings. Time complexity O(n^3).
//		// Approach 2: The idea is to use window sliding. Whenever we see repitition, we remove the pervious 
//		// occurrance and slide the window. Time complexity O(n^2).
////		String subString = LongestSubstringWithoutRepeatingCharacters.slidingWindow(str);
//		// Approach 3: linearTime solution. Time Complexity: O(n + d) where n is length of the input string 
//		// and d is number of characters in input string alphabet. For example, if string consists of lowercase 
//		// English characters then value of d is 26. Auxiliary Space: O(d) 
//		String subString = LongestSubstringWithoutRepeatingCharacters.linearTime(str);
//		System.out.println("subString: " + subString);
		
		
	}

	public static void printArray(int[] arr) {
		for (int i = 0; i < arr.length; i++) {
			System.out.print(arr[i] + " ");
		}
		System.out.println();
	}

}
