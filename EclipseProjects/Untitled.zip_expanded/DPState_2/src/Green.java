
public class Green implements State {
	
    public void change(TrafficLight light) {
        light.state = new Yellow();
    }

    public void ReportState() {
        System.out.println("Green light");
    }
}
