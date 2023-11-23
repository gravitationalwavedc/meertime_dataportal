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
    mainProject: { type: "String", defaultValue: "MEERTIME" }
    project: { type: "String", defaultValue: "All" }
    band: { type: "String", defaultValue: "All" }
  ) {
    searchmodeObservations(
      mainProject: $mainProject
      project: $project
      band: $band
    ) {
      totalObservations
      totalPulsars
      edges {
        node {
          jname
          latestObservation
          firstObservation
          project
          timespan
          numberOfObservations
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

  const rows = fragmentData.searchmodeObservations.edges.reduce(
    (result, edge) => {
      const row = { ...edge.node };
      row.projectKey = mainProject;
      row.latestObservation = formatUTC(row.latestObservation);
      row.firstObservation = formatUTC(row.firstObservation);
      row.action = (
        <ButtonGroup vertical>
          <Link
            to={`/search/${mainProject}/${row.jname}/`}
            size="sm"
            variant="outline-secondary"
            as={Button}
          >
            View all
          </Link>
          <Button
            href={kronosLink(row.beam, row.jname, row.latestObservation)}
            as="a"
            size="sm"
            variant="outline-secondary"
          >
            View last
          </Button>
        </ButtonGroup>
      );
      return [...result, { ...row }];
    },
    []
  );

  const columns = [
    { dataField: "jname", text: "JName", sort: true },
    {
      dataField: "project",
      text: "Project",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
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

  const summaryData = [
    {
      title: "Observations",
      value: fragmentData.searchmodeObservations.totalObservations,
    },
    {
      title: "Pulsars",
      value: fragmentData.searchmodeObservations.totalPulsars,
    },
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
