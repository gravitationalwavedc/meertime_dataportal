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
  subprojects: ["All", "Mo-NS", "Mo-EW"],
  bandOptions: ["All", "UHF-NS", "UHF-EW"],
  columns: [
    {
      dataField: "key",
      text: "",
      sort: false,
      hidden: true,
      toggle: false,
      csvExport: false,
    },
    {
      dataField: "plotLink",
      text: "",
      sort: false,
      hidden: true,
      toggle: false,
      csvExport: false,
    },
    {
      dataField: "utc",
      text: "Timestamp",
      sort: true,
      headerClasses: "fold-detail-utc",
    },
    {
      dataField: "project",
      text: "Project",
      sort: true,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
    },
    {
      dataField: "length",
      text: "Length",
      sort: true,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
      formatter: (cell) => `${cell} [s]`,
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "beam",
      text: "Beam",
      sort: true,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "bw",
      text: "BW",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "nchan",
      text: "Nchan",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "band",
      text: "Band",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
    },
    {
      dataField: "nbin",
      text: "Nbin",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "dmMeerpipe",
      text: "DM psrcat",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "snMeerpipe",
      text: "S/N raw",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "snBackend",
      text: "S/N cleaned",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "action",
      text: "",
      sort: false,
      align: "right",
      headerAlign: "right",
      csvExport: false,
    },
  ],
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
  bandOptions: ["All", "L-BAND", "UHF", "S-BAND", "UNKNOWN"],
  columns: [
    {
      dataField: "key",
      text: "",
      sort: false,
      hidden: true,
      toggle: false,
      csvExport: false,
    },
    {
      dataField: "plotLink",
      text: "",
      sort: false,
      hidden: true,
      toggle: false,
      csvExport: false,
    },
    {
      dataField: "observation.utcStart",
      text: "Timestamp",
      sort: true,
      headerClasses: "fold-detail-utc",
    },
    {
      dataField: "observation.project.short",
      text: "Project",
      sort: true,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
    },
    {
      dataField: "observation.duration",
      text: "Length",
      sort: true,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
      formatter: (cell) => `${parseFloat(cell / 60).toFixed(2)} [m]`,
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "observation.beam",
      text: "Beam",
      sort: true,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "observation.bandwidth",
      text: "BW",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "observation.nchan",
      text: "Nchan",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "observation.band",
      text: "Band",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
    },
    {
      dataField: "observation.foldNbin",
      text: "Nbin",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "observation.nant",
      text: "Nant",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "observation.nantEff",
      text: "Nant eff",
      sort: true,
      screenSizes: ["xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "observation.ephemeris.dm",
      text: "DM backend",
      sort: true,
      screenSizes: ["xl", "xxl"],
      align: "right",
      headerAlign: "right",
      formatter: (cell) => parseFloat(cell).toFixed(4),
    },
    {
      dataField: "pipelineRun.dm",
      text: "DM fit",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
      formatter: (cell) => parseFloat(cell).toFixed(4),
    },
    {
      dataField: "pipelineRun.rm",
      text: "RM ",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
      formatter: (cell) => parseFloat(cell).toFixed(2),
    },
    // {
    //   dataField: "snBackend",
    //   text: "S/N backend",
    //   sort: true,
    //   screenSizes: ["xxl"],
    //   align: "right",
    //   headerAlign: "right",
    // },
    {
      dataField: "pipelineRun.sn",
      text: "S/N",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
      formatter: (cell) => parseFloat(cell).toFixed(1),
    },
    {
      dataField: "action",
      text: "",
      sort: false,
      align: "right",
      headerAlign: "right",
      csvExport: false,
    },
  ],
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
