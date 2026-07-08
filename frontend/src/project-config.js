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
