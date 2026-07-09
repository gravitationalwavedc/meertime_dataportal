export const configuredMainProjectNames = (projects) => [
  ...new Set(
    projects.map((project) => project.mainProject?.name).filter(Boolean)
  ),
];

export const selectConfiguredMainProject = (projects, selected = "") => {
  const names = configuredMainProjectNames(projects);
  const selectedName = names.find(
    (name) => name.toLowerCase() === selected?.toLowerCase()
  );

  return selectedName || names[0] || "";
};

export const groupProjectsByMainProject = (projects) =>
  projects.reduce((groups, project) => {
    const name = project.mainProject?.name;

    // Build an object keyed by MainProject name, preserving the incoming
    // project order within each group. Projects without a MainProject name
    // cannot be shown under an optgroup, so leave the accumulator unchanged.
    return name
      ? { ...groups, [name]: [...(groups[name] || []), project] }
      : groups;
  }, {});
