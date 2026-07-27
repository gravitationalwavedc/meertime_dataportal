import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

vi.mock("./PlotlyPlot", () => ({
  default: ({ activePlot }) => <div>Rendered {activePlot}</div>,
}));
vi.mock("react-plotly.js", () => ({ default: () => null }));
vi.mock("plotly.js", () => ({ default: {} }));

import PlotContainer from "./PlotContainer";

const defaultProps = {
  jname: "J0125-2327",
  mainProject: "Synthetic",
  minimumSNR: 8,
  setMinimumSNR: vi.fn(),
  excludeBadges: [],
  setExcludeBadges: vi.fn(),
  allProjects: ["SYN"],
  mostCommonProject: "SYN",
  allNchans: [32],
};

describe("PlotContainer", () => {
  it("renders configured plot choices", () => {
    render(<PlotContainer {...defaultProps} plotTypes={["S/N", "DM"]} />);

    expect(screen.getByRole("option", { name: "S/N" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "DM" })).toBeInTheDocument();
    expect(
      screen.queryByRole("option", { name: "Timing Residuals" })
    ).not.toBeInTheDocument();
  });

  it("resets an unavailable active plot to the first configured plot", async () => {
    const { rerender } = render(
      <PlotContainer {...defaultProps} plotTypes={["DM", "RM"]} />
    );

    await userEvent.selectOptions(screen.getByLabelText("Y Axis"), "RM");
    rerender(<PlotContainer {...defaultProps} plotTypes={["S/N"]} />);

    expect(screen.getByLabelText("Y Axis")).toHaveValue("S/N");
    expect(screen.getByText("Rendered S/N")).toBeInTheDocument();
  });

  it("renders an empty state when no plots are configured", () => {
    render(<PlotContainer {...defaultProps} plotTypes={[]} />);

    expect(screen.getByText("No plots configured")).toBeInTheDocument();
    expect(screen.queryByLabelText("Y Axis")).not.toBeInTheDocument();
  });
});
