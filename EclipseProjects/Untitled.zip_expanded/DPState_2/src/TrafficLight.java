
public class TrafficLight {
	State state;

	public TrafficLight() {
		state = new Red();
	}
	
    public void change() {
        state.change(this);
    }
    
    public void Reportstate() {
        state.ReportState();
    }
}
