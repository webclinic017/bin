package av_stack;

import java.util.*;
/////////////////////////////// CHILD OF NGR /////////////////////////////////
public class NGL {
	
	public static int[] ngl(int[] arr) {
		Stack<Integer> stack = new Stack<>();
		int[] result = new int[arr.length];
//		for (int i = arr.length - 1; i >= 0; i--) {
		for (int i = 0; i < arr.length; i++) {
			if (stack.isEmpty()) {
				result[i] = -1;
			} else if (stack.peek() > arr[i]) {
				result[i] = stack.peek();
			} else if (stack.peek() <= arr[i]) {
				while (!stack.isEmpty() && stack.peek() <= arr[i]) {
					stack.pop();
				}
				if (stack.isEmpty()) {
					result[i] = -1;
				} else {
					result[i] = stack.peek();
				}
			}
			stack.push(arr[i]);
		}
		return result;
	}

}
