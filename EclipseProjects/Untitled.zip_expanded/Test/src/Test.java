
public class Test {

	public static void main(String[] args) {
		printPattern(5);
	}

	private static void printPattern(int n) {
		if (n == 1) {
			System.out.print("*-*");
			System.out.println();
		} else {
			int x = (n + 2)/2;
			for (int i = 1; i <= x; i++) {
				for (int j = 1; j <= n + i; j++) {
					System.out.print(" ");
				}
				for (int j = 1; j <= (2 * (n-i-1) + 1); j++) {
					System.out.print("*");
				}
				System.out.println();
			}
			int y = (n/2) + 1;
			for (int i = 1; i <= y; i++) {
				System.out.print(" ");
			}
			System.out.print("*");
			for (int i = 1; i <= n; i++) {
				System.out.print("-");
			}
			System.out.print("*");
			System.out.println();
			for (int i = x; i >= 1; i--) {
				for (int j = 1; j <= i - 1; j++) {
					System.out.print(" ");
				}
				for (int j = 1; j <= (2 * (n-i-1) + 1); j++) {
					System.out.print("*");
				}
				System.out.println();
			}
		}
	}
	
}
