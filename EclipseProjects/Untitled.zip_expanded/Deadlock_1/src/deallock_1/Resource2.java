package deallock_1;

public class Resource2 {
	boolean isLocked = false;
	
	synchronized void first(Resource1 a) {
		isLocked = true;
		String name = Thread.currentThread().getName();
		System.out.println(name + " entered Resource2.bar");
		while (!a.isLocked) {
			try {
				Thread.sleep(1000);
			} catch(InterruptedException e) {
				System.out.println("Resource2 Interrupted");
			}
		}
		System.out.println(name + " trying to call Resource1.last()");
		a.last();
	}
	synchronized void last() {
		System.out.println("Inside Resource1.last");
	}
}
