import { render, screen, within } from "@testing-library/react";
import ListControls from "./ListControls";
import { useProjectConfig } from "../context/project-config-context";

vi.mock("../context/project-config-context", () => ({
  useProjectConfig: vi.fn(),
}));

const configuredProjects = [
  {
    short: "ALPHA",
    bandOptions: ["LOW", "MID"],
    mainProject: { name: "Alpha", telescope: { name: "Alpha Telescope" } },
  },
  {
    short: "BETA",
    bandOptions: ["HIGH"],
    mainProject: { name: "Beta", telescope: { name: "Beta Telescope" } },
  },
  {
    short: "ALPHA_EXTRA",
    bandOptions: ["MID", "HIGH"],
    mainProject: { name: "Alpha", telescope: { name: "Alpha Telescope" } },
  },
];

const renderControls = (props = {}) =>
  render(
    <ListControls
      mainProject="Alpha"
      project="All"
      band="All"
      handleMainProjectFilter={vi.fn()}
      handleProjectFilter={vi.fn()}
      handleBandFilter={vi.fn()}
      searchProps={{ onSearch: vi.fn() }}
      columnToggleProps={{ columns: [] }}
      exportCSVProps={{}}
      {...props}
    />
  );

const selectOptions = (label) =>
  within(screen.getByLabelText(label))
    .queryAllByRole("option")
    .map(({ value, textContent }) => [value, textContent]);

describe("list controls component", () => {
  beforeEach(() => {
    useProjectConfig.mockReturnValue({
      projects: configuredProjects,
    });
  });

  it("renders catalogue filters from project configuration", () => {
    renderControls({ handleMostCommonProjectFilter: vi.fn() });

    expect(selectOptions("Main Project")).toEqual([
      ["Alpha", "Alpha Telescope"],
      ["Beta", "Beta Telescope"],
    ]);
    expect(selectOptions("Project")).toEqual([
      ["All", "All"],
      ["ALPHA", "ALPHA"],
      ["ALPHA_EXTRA", "ALPHA_EXTRA"],
    ]);
    expect(selectOptions("Band")).toEqual([
      ["All", "All"],
      ["LOW", "LOW"],
      ["MID", "MID"],
      ["HIGH", "HIGH"],
    ]);
  });

  it("renders empty filter choices when no projects are configured", () => {
    useProjectConfig.mockReturnValue({ projects: [], isLoading: false });

    renderControls();

    expect(selectOptions("Main Project")).toEqual([]);
    expect(selectOptions("Project")).toEqual([["All", "All"]]);
    expect(selectOptions("Band")).toEqual([["All", "All"]]);
  });
});
