
public class Red implements State {
	
    public void change(TrafficLight light) {
        light.state = new Green();
    }

    public void ReportState() {
        System.out.println("Red Light");
    }
}
