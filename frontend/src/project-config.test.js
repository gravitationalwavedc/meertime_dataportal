import {
  groupProjectsByMainProject,
  selectConfiguredMainProject,
} from "./project-config";

const projects = [
  { mainProject: { name: "Alpha" } },
  { mainProject: { name: "Beta" } },
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
});
