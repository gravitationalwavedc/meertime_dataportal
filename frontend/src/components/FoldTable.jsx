import { Button, ButtonGroup } from "react-bootstrap";
import { useEffect, useState } from "react";
import { columnsSizeFilter, formatUTC } from "../helpers";
import { graphql, useRefetchableFragment } from "react-relay";
import DataView from "./DataView";
import { Link } from "found";
import { useScreenSize } from "../context/screenSize-context";

const foldTableQuery = graphql`
  fragment FoldTable_data on Query
  @refetchable(queryName: "FoldTableRefetchQuery")
  @argumentDefinitions(
    mainProject: { type: "String", defaultValue: "MEERTIME" }
    project: { type: "String", defaultValue: "All" }
    band: { type: "String", defaultValue: "All" }
  ) {
    foldObservations(
      mainProject: $mainProject
      project: $project
      band: $band
    ) {
      totalObservations
      totalPulsars
      totalObservationTime
      totalProjectTime
      edges {
        node {
          jname
          beam
          latestObservation
          firstObservation
          allProjects
          project
          timespan
          numberOfObservations
          lastSnRaw
          highestSnRaw
          lowestSnRaw
          lastIntegrationMinutes
          maxSnPipe
          avgSnPipe
          totalIntegrationHours
        }
      }
    }
  }
`;

const FoldTable = ({
  data,
  match: {
    location: { query },
  },
}) => {
  const [relayData, refetch] = useRefetchableFragment(foldTableQuery, data);

  const { screenSize } = useScreenSize();
  const [mainProject, setMainProject] = useState(
    query.mainProject || "meertime"
  );
  const [project, setProject] = useState(query.project || "All");
  const [band, setBand] = useState(query.band || "All");

  useEffect(() => {
    refetch({ mainProject: mainProject, project: project, band: band });
    const url = new URL(window.location);
    url.searchParams.set("mainProject", mainProject);
    url.searchParams.set("project", project);
    url.searchParams.set("band", band);
    window.history.pushState({}, "", url);
  }, [band, project, mainProject, query, refetch]);

  const handleMainProjectChange = (newMainProject) => {
    setMainProject(newMainProject);
    setProject("All");
    setBand("All");
  };

  const rows = relayData.foldObservations.edges.reduce((result, edge) => {
    const row = { ...edge.node };
    row.projectKey = mainProject;
    row.latestObservation = formatUTC(row.latestObservation);
    row.firstObservation = formatUTC(row.firstObservation);
    row.action = (
      <ButtonGroup vertical>
        <Link
          to={`/fold/${mainProject}/${row.jname}/`}
          size="sm"
          variant="outline-secondary"
          as={Button}
        >
          View all
        </Link>
        <Link
          to={`/${row.jname}/${row.latestObservation}/${row.beam}/`}
          size="sm"
          variant="outline-secondary"
          as={Button}
        >
          View last
        </Link>
      </ButtonGroup>
    );
    return [...result, { ...row }];
  }, []);

  const columns = [
    {
      dataField: "projectKey",
      hidden: true,
      toggle: false,
      sort: false,
      csvExport: false,
    },
    { dataField: "jname", text: "JName", sort: true },
    {
      dataField: "project",
      text: "Project",
      sort: true,
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "allProjects",
      text: "All Projects",
      sort: true,
      screenSizes: ["xxl"],
    },
    { dataField: "latestObservation", text: "Last", sort: true },
    {
      dataField: "firstObservation",
      text: "First",
      sort: true,
      screenSizes: ["xxl"],
    },
    {
      dataField: "timespan",
      text: "Timespan",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["md", "lg", "xl", "xxl"],
      formatter: (cell) => `${cell} [d]`,
    },
    {
      dataField: "numberOfObservations",
      text: "Observations",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["md", "lg", "xl", "xxl"],
    },
    {
      dataField: "totalIntegrationHours",
      text: "Total int",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      formatter: (cell) => `${cell} [h]`,
    },
    {
      dataField: "lastSnRaw",
      text: "Last S/N raw",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
    },
    {
      dataField: "highestSnRaw",
      text: "High S/N raw",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
    },
    {
      dataField: "lowestSnRaw",
      text: "Low S/N raw",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
    },
    {
      dataField: "lastIntegrationMinutes",
      text: "Last int.",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      formatter: (cell) => `${cell} [m]`,
    },
    {
      dataField: "action",
      text: "",
      align: "right",
      headerAlign: "right",
      csvExport: false,
      sort: false,
    },
  ];

  const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

  const summaryData = [
    {
      title: "Observations",
      value: relayData.foldObservations.totalObservations,
    },
    { title: "Unique Pulsars", value: relayData.foldObservations.totalPulsars },
    {
      title: "Pulsar Hours",
      value: relayData.foldObservations.totalObservationTime,
    },
  ];

  if (project !== "All") {
    summaryData.push({
      title: "Project Hours",
      value: relayData.foldObservations.totalProjectTime,
    });
  }

  return (
    <DataView
      summaryData={summaryData}
      columns={columnsSizeFiltered}
      rows={rows}
      setProject={setProject}
      project={project}
      mainProject={mainProject}
      setMainProject={handleMainProjectChange}
      band={band}
      setBand={setBand}
      query={query}
      mainProjectSelect
      rememberSearch={true}
    />
  );
};

export default FoldTable;
