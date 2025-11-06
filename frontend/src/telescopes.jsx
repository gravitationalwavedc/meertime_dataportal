const getSubProjectOptions = (subprojects) =>
  subprojects.map((subproject) => (
    <option value={subproject} key={subproject}>
      {subproject}
    </option>
  ));

const getProject = (projectValue) =>
  projectValue === molonglo.value ? molonglo : meertime;

const molonglo = {
  value: "MONSPSR",
  title: "Molonglo",
  subprojects: ["All", "MONSPSR_TIMING"],
  bandOptions: ["All", "UHF_NS"],
  plotTypes: ["Timing Residuals", "Flux Density", "S/N"],
};

const meertime = {
  value: "meertime",
  title: "MeerKAT",
  subprojects: [
    "All",
    "TPA",
    "TPA2",
    "COWD",
    "DNS",
    "NGC1851E",
    "J1902-5105",
    "J1227-6208",
    "J0737-3039A",
    "RelBin",
    "PTA",
    "PTA2",
    "GC",
    "NGC6440",
  ],
  bandOptions: [
    "All",
    "LBAND",
    "UHF",
    "SBAND_0",
    "SBAND_1",
    "SBAND_2",
    "SBAND_3",
    "SBAND_4",
  ],
  plotTypes: ["Timing Residuals", "Flux Density", "S/N", "DM", "RM"],
};

const allProjects = [meertime, molonglo];

const projectOptions = allProjects.map((project) => (
  <option value={project.value} key={project.value}>
    {project.title}
  </option>
));

export { molonglo, meertime, getProject, getSubProjectOptions, projectOptions };
