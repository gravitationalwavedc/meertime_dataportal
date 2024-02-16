import { Button, ButtonGroup } from "react-bootstrap";
import { useEffect, useState } from "react";
import { columnsSizeFilter, formatUTC } from "../helpers";
import { graphql, useRefetchableFragment } from "react-relay";
import DataView from "./DataView";
import { Link } from "found";
import { useScreenSize } from "../context/screenSize-context";

const FoldTableFragment = graphql`
  fragment FoldTableFragment on Query
  @refetchable(queryName: "FoldTableRefetchQuery")
  @argumentDefinitions(
    pulsar: { type: "String", defaultValue: "All" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
    mostCommonProject: { type: "String", defaultValue: "All" }
    project: { type: "String", defaultValue: "All" }
    band: { type: "String", defaultValue: "All" }
  ) {
    observationSummary(
      pulsar_Name: $pulsar
      obsType: "fold"
      calibration_Id: "All"
      mainProject: $mainProject
      project_Short: $project
      band: $band
    ) {
      edges {
        node {
          observations
          pulsars
          observationHours
        }
      }
    }
    pulsarFoldSummary(
      mainProject: $mainProject
      mostCommonProject: $mostCommonProject
      project: $project
      band: $band
    ) {
      edges {
        node {
          pulsar {
            name
          }
          latestObservation
          latestObservationBeam
          firstObservation
          allProjects
          mostCommonProject
          timespan
          numberOfObservations
          lastSn
          highestSn
          lowestSn
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
  const [relayData, refetch] = useRefetchableFragment(FoldTableFragment, data);

  const { screenSize } = useScreenSize();
  const [mainProject, setMainProject] = useState(
    query.mainProject || "meertime"
  );
  const [mostCommonProject, setMostCommonProject] = useState(
    query.mostCommonProject || "All"
  );
  const [project, setProject] = useState(query.project || "All");
  const [band, setBand] = useState(query.band || "All");

  const handleRefetch = ({
    newMainProject = mainProject,
    newProject = project,
    newMostCommonProject = mostCommonProject,
    newBand = band,
  } = {}) => {
    const url = new URL(window.location);
    url.searchParams.set("mainProject", newMainProject);
    url.searchParams.set("mostCommonProject", newMostCommonProject);
    url.searchParams.set("project", newProject);
    url.searchParams.set("band", newBand);
    window.history.pushState({}, "", url);
    refetch({
      mainProject: newMainProject,
      mostCommonProject: newMostCommonProject,
      project: newProject,
      band: newBand,
    });
  };

  const handleMainProjectChange = (newMainProject) => {
    const newMostCommonProject = "All";
    const newProject = "All";
    const newBand = "All";
    setMainProject(newMainProject);
    setMostCommonProject(newMostCommonProject);
    setProject(newProject);
    setBand(newBand);
    handleRefetch({
      newMainProject: newMainProject,
      newMostCommonProject: newMostCommonProject,
      newProject: newProject,
      newBand: newBand,
    });
  };

  const handleMostCommonProjectChange = (newMostCommonProject) => {
    const newProject = "All";
    setMostCommonProject(newMostCommonProject);
    setProject(newProject);
    handleRefetch({
      newMostCommonProject: newMostCommonProject,
      newProject: newProject,
    });
  };

  const handleProjectChange = (newProject) => {
    const newMostCommonProject = "All";
    setMostCommonProject(newMostCommonProject);
    setProject(newProject);
    handleRefetch({
      newMostCommonProject: newMostCommonProject,
      newProject: newProject,
    });
  };

  const handleBandChange = (newBand) => {
    setProject(newBand);
    handleRefetch({ newBand: newBand });
  };

  const rows = relayData.pulsarFoldSummary.edges.reduce((result, edge) => {
    const row = { ...edge.node };
    row.projectKey = mainProject;
    row.latestObservation = formatUTC(row.latestObservation);
    row.firstObservation = formatUTC(row.firstObservation);
    row.jname = row.pulsar.name;
    row.action = (
      <ButtonGroup vertical>
        <Link
          to={`/fold/${mainProject}/${row.pulsar.name}/`}
          size="sm"
          variant="outline-secondary"
          as={Button}
        >
          View all
        </Link>
        <Link
          to={`/${mainProject}/${row.jname}/${row.latestObservation}/${row.latestObservationBeam}/`}
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
      dataField: "mostCommonProject",
      text: "Most Common Project",
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
      formatter: (cell) => `${parseFloat(cell).toFixed(1)} [h]`,
    },
    {
      dataField: "lastSn",
      text: "Last S/N",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      formatter: (cell) => parseFloat(cell).toFixed(1),
    },
    {
      dataField: "highestSn",
      text: "High S/N",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      formatter: (cell) => parseFloat(cell).toFixed(1),
    },
    {
      dataField: "lowestSn",
      text: "Low S/N",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      formatter: (cell) => parseFloat(cell).toFixed(1),
    },
    {
      dataField: "lastIntegrationMinutes",
      text: "Last int.",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      formatter: (cell) => `${parseFloat(cell * 60).toFixed(2)} [s]`,
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

  const summaryNode = relayData.observationSummary.edges[0]?.node;
  const summaryData = [
    { title: "Observations", value: summaryNode.observations },
    { title: "Unique Pulsars", value: summaryNode.pulsars },
    { title: "Observation Hours", value: summaryNode.observationHours },
  ];

  return (
    <DataView
      summaryData={summaryData}
      columns={columnsSizeFiltered}
      rows={rows}
      mainProject={mainProject}
      setMainProject={handleMainProjectChange}
      mostCommonProject={mostCommonProject}
      setMostCommonProject={handleMostCommonProjectChange}
      project={project}
      setProject={handleProjectChange}
      band={band}
      setBand={handleBandChange}
      query={query}
      mainProjectSelect
      rememberSearch={true}
    />
  );
};

export default FoldTable;
