import { render, screen, within } from "@testing-library/react";
import JoinProjectForm from "./JoinProjectForm";
import { useFragment } from "react-relay";

vi.mock("react-relay", () => ({
  commitMutation: vi.fn(),
  graphql: vi.fn(),
  useFragment: vi.fn(),
}));

const projectConfiguration = {
  projectConfiguration: {
    edges: [
      {
        node: {
          code: "ALPHA_ONE",
          short: "A1",
          description: "Alpha project",
          mainProject: { name: "Alpha", telescope: { name: "Scope One" } },
        },
      },
      {
        node: {
          code: "BETA_ONE",
          short: "B1",
          description: "Beta project",
          mainProject: { name: "Beta", telescope: { name: "Scope Two" } },
        },
      },
    ],
  },
};

describe("JoinProjectForm", () => {
  beforeEach(() => {
    useFragment.mockReturnValue(projectConfiguration);
  });

  it("renders configured projects grouped by MainProject", () => {
    render(<JoinProjectForm relayData={projectConfiguration} />);

    const select = screen.getByLabelText("Project");
    const groups = [...select.querySelectorAll("optgroup")];

    expect(groups.map(({ label }) => label)).toEqual(["Alpha", "Beta"]);
    expect(
      within(groups[0]).getByRole("option", { name: "A1 - ALPHA_ONE" })
    ).toBeInTheDocument();
    expect(
      within(groups[1]).getByRole("option", { name: "B1 - BETA_ONE" })
    ).toBeInTheDocument();
  });
});
