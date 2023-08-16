import { fireEvent, render } from "@testing-library/react";
import Ephemeris from "./Ephemeris";

describe("ephemeris modal component", () => {
  it("should render the table", () => {
    expect.hasAssertions();
    const { getByText } = render(
      <Ephemeris
        ephemeris={'{"Data": ["an example", "another example"]}'}
        updated={{}}
        show={true}
        setShow={() => {}}
      />
    );
    expect(getByText("Folding Ephemeris")).toBeInTheDocument();
  });

  it("should close when the cross is clicked", () => {
    expect.hasAssertions();
    const setShow = vi.fn();
    const { getByRole } = render(
      <Ephemeris
        ephemeris={'{"Data": ["an example", "another example"]}'}
        updated={{}}
        show={true}
        setShow={setShow}
      />
    );
    const closeButton = getByRole("button");
    fireEvent.click(closeButton);
    expect(setShow).toHaveBeenCalledWith(false);
  });
});
