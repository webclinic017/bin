package reqres.country;

import reqres.BaseResponse;

public class CreateCountryResponse extends BaseResponse {
	
	private static final long serialVersionUID = 4235996810315066531L;
	
	private int id;

	public int getId() {
		return id;
	}

	public void setId(int id) {
		this.id = id;
	}

	@Override
	public String toString() {
		return "CreateCountryResponse [id=" + id + "]";
	}
	
}
