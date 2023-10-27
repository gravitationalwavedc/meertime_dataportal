import { Button, ButtonGroup } from "react-bootstrap";
import { useEffect, useState } from "react";
import { columnsSizeFilter, formatUTC, kronosLink } from "../helpers";
import { graphql, useRefetchableFragment } from "react-relay";
import DataView from "./DataView";
import { Link } from "found";
import SearchmodeCard from "./SearchmodeCard";
import { useScreenSize } from "../context/screenSize-context";

const searchTableQuery = graphql`
  fragment SearchTable_data on Query
  @refetchable(queryName: "SearchTableQuery")
  @argumentDefinitions(
    mainProject: { type: "String", defaultValue: "MeerTIME" }
    project: { type: "String", defaultValue: "All" }
    mostCommonProject: { type: "String", defaultValue: "All" }
    pulsar: { type: "String", defaultValue: "All" }
    band: { type: "String", defaultValue: "All" }
  ) {
    observationSummary(
      pulsar_Name: $pulsar
      obsType: "search"
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
    pulsarSearchSummary(
      mainProject: $mainProject
      mostCommonProject: $mostCommonProject
      band: $band
    ) {
      totalObservations
      totalPulsars
      totalObservationTime
      totalProjectTime
      edges {
        node {
          pulsar {
            name
          }
          latestObservation
          firstObservation
          allProjects
          mostCommonProject
          timespan
          numberOfObservations
          lastIntegrationMinutes
          totalIntegrationHours
        }
      }
    }
  }
`;
const SearchTable = ({ data }) => {
  const [fragmentData, refetch] = useRefetchableFragment(
    searchTableQuery,
    data
  );
  const { screenSize } = useScreenSize();
  const [mainProject, setMainProject] = useState("meertime");
  const [project, setProject] = useState("All");
  const [band, setBand] = useState("All");

  useEffect(() => {
    refetch({ mainProject: mainProject, project: project, band: band });
  }, [band, mainProject, project, refetch]);

  console.log("searchData", fragmentData.observationSummary);
  console.log("observationData", fragmentData.pulsarSearchSummary);
  const rows = fragmentData.pulsarSearchSummary.edges.reduce((result, edge) => {
    const row = { ...edge.node };
    row.projectKey = mainProject;
    row.latestObservation = formatUTC(row.latestObservation);
    row.firstObservation = formatUTC(row.firstObservation);
    row.action = (
      <ButtonGroup vertical>
        <Link
          to={`/search/${mainProject}/${row.pulsar.name}/`}
          size="sm"
          variant="outline-secondary"
          as={Button}
        >
          View all
        </Link>
        <Button
          href={kronosLink(row.beam, row.pulsar.name, row.latestObservation)}
          as="a"
          size="sm"
          variant="outline-secondary"
        >
          View last
        </Button>
      </ButtonGroup>
    );
    return [...result, { ...row }];
  }, []);

  const columns = [
    { dataField: "pulsar.name", text: "JName", sort: true },
    {
      dataField: "mostCommonProject",
      text: "Most Common Project",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
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
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "timespan",
      text: "Timespan",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => `${cell} [d]`,
      screenSizes: ["md", "lg", "xl", "xxl"],
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
      sort: false,
    },
  ];

  const columnsForScreenSize = columnsSizeFilter(columns, screenSize);

  const summaryNode = fragmentData.observationSummary.edges[0]?.node;
  const summaryData = [
    { title: "Observations", value: summaryNode.observations },
    { title: "Pulsars", value: summaryNode.pulsars },
  ];

  return (
    <div className="searchmode-table">
      <DataView
        summaryData={summaryData}
        columns={columnsForScreenSize}
        rows={rows}
        setProject={setProject}
        project={project}
        mainProject={mainProject}
        setMainProject={setMainProject}
        setBand={setBand}
        card={SearchmodeCard}
      />
    </div>
  );
};

export default SearchTable;
