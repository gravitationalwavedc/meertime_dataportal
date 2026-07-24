import {
  mainProjectAllowsDownloads,
  mainProjectShowsExtendedObservationFields,
  projectAllowsDownloads,
  groupProjectsByMainProject,
  selectConfiguredMainProject,
} from "./project-config";

const projects = [
  {
    code: "A-1",
    short: "A1",
    allowDownloads: true,
    showExtendedObservationFields: true,
    mainProject: { name: "Alpha" },
  },
  {
    code: "B-1",
    short: "B1",
    allowDownloads: false,
    showExtendedObservationFields: false,
    mainProject: { name: "Beta" },
  },
];

describe("project configuration selectors", () => {
  it("uses the first configured MainProject when no selection is provided", () => {
    expect(selectConfiguredMainProject(projects)).toBe("Alpha");
  });

  it("uses the first configured MainProject when the selection is invalid", () => {
    expect(selectConfiguredMainProject(projects, "Unknown")).toBe("Alpha");
  });

  it("preserves valid selections using configured casing", () => {
    expect(selectConfiguredMainProject(projects, "beta")).toBe("Beta");
  });

  it("returns an empty selection when no projects are configured", () => {
    expect(selectConfiguredMainProject([], "Alpha")).toBe("");
  });

  it("groups projects by MainProject in configuration order", () => {
    expect(groupProjectsByMainProject(projects)).toEqual({
      Alpha: [projects[0]],
      Beta: [projects[1]],
    });
  });

  it("checks download availability for a specific configured project", () => {
    expect(
      projectAllowsDownloads(projects, {
        code: "B-1",
        short: "B1",
        mainProject: { name: "Beta" },
      })
    ).toBe(false);
  });

  it("checks download availability for any configured project in a MainProject", () => {
    expect(mainProjectAllowsDownloads(projects, "Alpha")).toBe(true);
    expect(mainProjectAllowsDownloads(projects, "Beta")).toBe(false);
  });

  it("checks extended observation field visibility for a configured MainProject", () => {
    expect(mainProjectShowsExtendedObservationFields(projects, "Alpha")).toBe(
      true
    );
    expect(mainProjectShowsExtendedObservationFields(projects, "Beta")).toBe(
      false
    );
  });
});
