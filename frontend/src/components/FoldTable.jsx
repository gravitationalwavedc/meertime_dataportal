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
  console.log("data:", data);
  const [relayData, refetch] = useRefetchableFragment(FoldTableFragment, data);
  console.log("observationData:", relayData.observationSummary);
  console.log("relayData:", relayData.pulsarFoldSummary);

  const { screenSize } = useScreenSize();
  const [mainProject, setMainProject] = useState(
    query.mainProject || "meertime"
  );
  const [project, setProject] = useState(query.project || "All");
  const [band, setBand] = useState(query.band || "All");

  useEffect(() => {
    refetch({
      mainProject: mainProject,
      project: project,
      band: band,
    });
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
          to={`/${row.jname}/${row.latestObservation}/${row.latestObservationBeam}/`}
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
      formatter: (cell) => `${parseFloat(cell).toFixed(2)} [m]`,
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

  console.log(relayData.observationSummary);
  const summaryNode = relayData.observationSummary.edges[0]?.node;
  console.log(summaryNode);
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
