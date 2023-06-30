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
  data: { foldPulsarSummary: relayData },
  relay,
  match: {
    location: { query },
  },
}) => {
  const [relayData, refetch] = useRefetchableFragment(foldTableQuery, data);

  const { screenSize } = useScreenSize();
  const [mainProject, setMainProject] = useState(
    query.mainProject || "meertime"
  );
  const [mostCommonProject, setMostCommonProject] = useState(query.mostCommonProject || "All");
  const [band, setBand] = useState(query.band || "All");

  useEffect(() => {
    relay.refetch({ mainProject: mainProject, mostCommonProject: mostCommonProject, band: band });
    const url = new URL(window.location);
    url.searchParams.set("mainProject", mainProject);
    url.searchParams.set("mostCommonProject", mostCommonProject);
    url.searchParams.set("band", band);
    window.history.pushState({}, "", url);
  }, [band, mostCommonProject, mainProject, query, relay]);

  const handleMainProjectChange = (newMainProject) => {
    setMainProject(newMainProject);
    setMostCommonProject("All");
    setBand("All");
  };

  const rows = relayData.foldObservations.edges.reduce((result, edge) => {
    const row = { ...edge.node };
    row.projectKey = mainProject;
    row.latestObservation = formatUTC(row.latestObservation);
    row.firstObservation = formatUTC(row.firstObservation);
    row.jname = row.pulsar.name;
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

  if (mostCommonProject !== "All") {
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
      setMostCommonProject={setMostCommonProject}
      mostCommonProject={mostCommonProject}
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

export default createRefetchContainer(
  FoldTable,
  {
    data: graphql`
      fragment FoldTable_data on Query
      @argumentDefinitions(
        mainProject: { type: "String", defaultValue: "MeerTIME" }
        mostCommonProject: { type: "String", defaultValue: "All" }
        band: { type: "String", defaultValue: "All" }
      ) {
        foldPulsarSummary (
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
              pulsar {name}
              latestObservation
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
    `,
  },
  graphql`
    query FoldTableRefetchQuery(
      $mainProject: String
      $mostCommonProject: String
      $band: String
    ) {
      ...FoldTable_data
        @arguments(mainProject: $mainProject, mostCommonProject: $mostCommonProject, band: $band)
    }
  `
);
