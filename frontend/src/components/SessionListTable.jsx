import { Button, ButtonGroup } from "react-bootstrap";
import { useState } from "react";
import { graphql, useFragment } from "react-relay";
import DataView from "./DataView";
import { Link } from "found";
import { formatUTC } from "../helpers";

const sessionListTableQuery = graphql`
  fragment SessionListTable_data on Query {
    calibration {
      edges {
        node {
          id
          idInt
          start
          end
          allProjects
          nObservations
          nAntMin
          nAntMax
          totalIntegrationTimeSeconds
        }
      }
    }
  }
`;

const SessionListTable = ({ data }) => {
  const fragmentData = useFragment(sessionListTableQuery, data);

  const allRows = fragmentData.calibration.edges.reduce((result, edge) => {
    const row = { ...edge.node };
    console.log(row);
    row.start = formatUTC(row.start);
    row.end = formatUTC(row.end);
    row.key = `${row.start}-${row.end}`;
    row.action = (
      <ButtonGroup vertical>
        <Link
          to={`/session/${row.idInt}/`}
          size="sm"
          variant="outline-secondary"
          as={Button}
        >
          View all
        </Link>
      </ButtonGroup>
    );
    return [...result, { ...row }];
  }, []);

  const [rows, setRows] = useState(allRows);

  const columns = [
    {
      dataField: "key",
      sort: false,
      hidden: true,
      toggle: false,
      csvExport: false,
    },
    { dataField: "start", text: "Start" },
    { dataField: "end", text: "End" },
    { dataField: "allProjects", text: "Projects" },
    {
      dataField: "nObservations",
      text: "Observations",
      align: "right",
      headerAlign: "right",
    },
    // {
    //   dataField: "frequency",
    //   text: "Frequency",
    //   align: "right",
    //   headerAlign: "right",
    // },
    {
      dataField: "totalIntegrationTimeSeconds",
      text: "Total Int",
      formatter: (cell) => `${(parseFloat(cell) / 60).toFixed(1)} [m]`,
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "nAntMin",
      text: "N_ANT (min)",
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "nAntMax",
      text: "N_ANT (max)",
      align: "right",
      headerAlign: "right",
    },
    // {
    //   dataField: "zapFraction",
    //   text: "Zap fraction (%)",
    //   align: "right",
    //   headerAlign: "right",
    // },
    // { dataField: "listOfPulsars", hidden: true },
    {
      dataField: "action",
      text: "",
      align: "right",
      headerAlign: "right",
      sort: false,
    },
  ];

  const summaryData = [{ title: "Sessions", value: rows.length }];

  const handleProjectFilter = (project) => {
    if (project === "All") {
      setRows(allRows);
      return;
    }
    const newRows = allRows.filter((row) =>
      row.allProjects.toLowerCase().includes(project.toLowerCase())
    );
    setRows(newRows);
  };

  return (
    <DataView
      summaryData={summaryData}
      columns={columns}
      rows={rows}
      setProject={handleProjectFilter}
      keyField="key"
    />
  );
};

export default SessionListTable;
