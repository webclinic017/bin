
public class Yellow implements State {
    public void change(TrafficLight light)
    {
        light.state = new Red();
    }

    public void ReportState() {
        System.out.println("Yellow Light");
    }
}
