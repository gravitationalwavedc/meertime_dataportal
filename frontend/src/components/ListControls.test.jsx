import { fireEvent, render } from "@testing-library/react";
import ListControls from "./ListControls";

describe("list controls component", () => {
  it("should handle changes to proposals", () => {
    expect.hasAssertions();
    const handleProjectFilter = vi.fn();
    const { getByLabelText } = render(
      <ListControls
        handleProjectFilter={handleProjectFilter}
        handleBandFilter={vi.fn()}
        searchProps={{ onSearch: vi.fn() }}
        columnToggleProps={{ columns: [] }}
        exportCSVProps={{}}
      />
    );
    fireEvent.change(getByLabelText("Project"), { target: { value: "TPA" } });
    expect(handleProjectFilter).toHaveBeenCalledWith("TPA");
  });

  it("should handle changes to band", () => {
    expect.hasAssertions();
    const handleBandFilter = vi.fn();
    const { getByLabelText } = render(
      <ListControls
        handleProjectFilter={vi.fn()}
        handleBandFilter={handleBandFilter}
        searchProps={{ onSearch: vi.fn() }}
        columnToggleProps={{ columns: [] }}
        exportCSVProps={{}}
      />
    );
    fireEvent.change(getByLabelText("Band"), { target: { value: "UHF" } });
    expect(handleBandFilter).toHaveBeenCalledWith("UHF");
  });
});
