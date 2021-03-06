import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadFactory;
import java.util.stream.Collectors;

public class Main {

	//	private static List<Shop> shops = Arrays.asList(new Shop("1sShop"),
	//	new Shop("2ndShop"),
	//	new Shop("3rdShop"),
	//	new Shop("4thShop"));
	//
	//  private static List<Shop> shops = Arrays.asList(new Shop("1sShop"),
	//	new Shop("2ndShop"),
	//	new Shop("3rdShop"),
	//	new Shop("4thShop"),
	//	new Shop("5thShop"));
	//
	private static List<Shop> shops = Arrays.asList(new Shop("1sShop"),
			new Shop("2ndShop"),
			new Shop("3rdShop"),
			new Shop("4thShop"),
			new Shop("5thShop"),
			new Shop("6thShop"),
			new Shop("7thShop"),
			new Shop("8thShop"),
			new Shop("9thShop"));

	private static final Executor EXECUTOR = Executors.newFixedThreadPool(
			Math.min(shops.size(), 100), new ThreadFactory() {
				public Thread newThread(Runnable r) {
					Thread thread = new Thread(r);
					thread.setDaemon(true);
					return thread;
				}
			}
			);

	public static void main(String[] args) {
		System.out.println("+++++++++++++++++++++++++++++++++++++++++++++++++++++");
		System.out.println("number of processors available in this machine: "
				+ Runtime.getRuntime().availableProcessors());
		System.out.println("+++++++++++++++++++++++++++++++++++++++++++++++++++++");
		System.out.println();

		long start = System.nanoTime();

		// TRY ALL THESE VERSIONS OF findPrices() FOR ALL VERSIONS OF shops.
		//System.out.println(findPrices1("myPhone"));
		//System.out.println(findPrices2("myPhone"));
		//System.out.println(findPrices3("myPhone"));
		//System.out.println(findPrices4("myPhone"));
		System.out.println(findPrices5("myPhone"));

		long duration = (System.nanoTime() - start) / 1_000_000;
		System.out.println("Done in " + duration + " msecs");
	}

	public static List<String> findPrices1(String product) {
		return shops.stream()
				.map(shop -> String.format("%s price is %.2f",
						shop.getName(), shop.getPrice(product)))
				.collect(Collectors.toList());
	}

	public static List<String> findPrices2(String product) {
		return shops.parallelStream()
				.map(shop -> String.format("%s price is %.2f",
						shop.getName(), shop.getPrice(product)))
				.collect(Collectors.toList());
	}

	public static List<String> findPrices3(String product) {
		return	shops.stream()
				.map(shop -> CompletableFuture.supplyAsync(
						() -> String.format("%s price is %.2f",
								shop.getName(), shop.getPrice(product))))
				.map(CompletableFuture::join)
				.collect(Collectors.toList());
	}

	public static List<String> findPrices4(String product) {
		List<CompletableFuture<String>> priceFutures =
				shops.stream()
				.map(shop -> CompletableFuture.supplyAsync(
						() -> String.format("%s price is %.2f",
								shop.getName(), shop.getPrice(product))))
				.collect(Collectors.toList());

		return priceFutures.stream()
				.map(CompletableFuture::join)
				.collect(Collectors.toList());
	}

	public static List<String> findPrices5(String product) {
		List<CompletableFuture<String>> priceFutures =
				shops.stream()
				.map(shop -> CompletableFuture.supplyAsync(
						() -> String.format("%s price is %.2f",
								shop.getName(), shop.getPrice(product)), EXECUTOR))
				.collect(Collectors.toList());

		return priceFutures.stream()
				.map(CompletableFuture::join)
				.collect(Collectors.toList());
	}

}
