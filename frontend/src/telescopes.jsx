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

const trapum = {
  value: "trapum",
  title: "Trapum",
  subprojects: ["All"],
  bandOptions: [
    "All",
    "LBAND",
    "UHF",
    "SBAND_0",
    "SBAND_1",
    "SBAND_2",
    "SBAND_3",
    "SBAND_4",
    "UNKNOWN",
  ],
};

const meertime = {
  value: "meertime",
  title: "MeerTime",
  subprojects: [
    "All",
    "TPA",
    "RelBin",
    "PTA",
    "GC",
    "NGC6440",
    "MeerTime",
    "Flux",
    "Unknown",
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
    "UNKNOWN",
  ],
  plotTypes: ["Timing Residuals", "Flux Density", "S/N", "DM", "RM"],
};

const allProjects = [meertime, trapum, molonglo];

const projectOptions = allProjects.map((project) => (
  <option value={project.value} key={project.value}>
    {project.title}
  </option>
));

export {
  molonglo,
  trapum,
  meertime,
  getProject,
  getSubProjectOptions,
  projectOptions,
};
