import { useState } from "react";
import { graphql, useFragment } from "react-relay";
import { columnsSizeFilter, kronosLink } from "../helpers";
import Button from "react-bootstrap/Button";
import DataView from "./DataView";
import SearchmodeDetailCard from "./SearchmodeDetailCard";
import { formatUTC } from "../helpers";
import { useScreenSize } from "../context/screenSize-context";

const SearchDetailTableFragment = graphql`
  fragment SearchDetailTableFragment on Query
  @argumentDefinitions(
    jname: { type: "String", defaultValue: "" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
  ) {
    observationSummary(
      pulsar_Name: $jname
      obsType: "search"
      calibration_Id: ""
      mainProject: $mainProject
      project_Short: ""
      band: ""
    ) {
      edges {
        node {
          observations
          projects
          observationHours
          timespanDays
        }
      }
    }
    observation(
      pulsar_Name: [$jname]
      mainProject: $mainProject
      obsType: "search"
    ) {
      edges {
        node {
          id
          utcStart
          project {
            short
          }
          raj
          decj
          beam
          duration
          frequency
          nantEff
          filterbankNbit
          filterbankNpol
          filterbankNchan
          filterbankTsamp
          filterbankDm
        }
      }
    }
  }
`;

const formatCoordinate = (value, decimals = 2) => {
  if (!value) return value;
  const parts = String(value).split(":");
  if (parts.length !== 3) return value;

  const seconds = Number(parts[2]);
  if (Number.isNaN(seconds)) return value;

  return `${parts[0]}:${parts[1]}:${seconds.toFixed(decimals)}`;
};

const SearchDetailTable = ({ data, jname }) => {
  const { screenSize } = useScreenSize();
  const relayData = useFragment(SearchDetailTableFragment, data);
  const allRows = relayData.observation.edges.reduce((result, edge) => {
    const formattedRa = formatCoordinate(edge.node.raj);
    const formattedDec = formatCoordinate(edge.node.decj);

    return [
      ...result,
      {
        ...edge.node,
        key: `${edge.node.utcStart}:${edge.node.beam}`,
        jname: jname,
        utc: formatUTC(edge.node.utcStart),
        raj: formattedRa,
        decj: formattedDec,
        ra: formattedRa,
        dec: formattedDec,
        action: (
          <Button
            href={kronosLink(
              edge.node.beam,
              jname,
              formatUTC(edge.node.utcStart)
            )}
            as="a"
            size="sm"
            variant="outline-secondary"
          >
            View
          </Button>
        ),
      },
    ];
  }, []);

  const [rows, setRows] = useState(allRows);

  const columns = [
    {
      dataField: "key",
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
      dataField: "project.short",
      text: "Project",
      sort: true,
      screenSizes: ["md", "lg", "xl", "xxl"],
    },
    {
      dataField: "raj",
      text: "RA",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "decj",
      text: "DEC",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "duration",
      text: "Duration",
      sort: true,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
      formatter: (cell) => `${parseFloat(cell).toFixed(2)} [s]`,
    },
    {
      dataField: "beam",
      text: "Beam",
      sort: true,
      screenSizes: ["lg", "xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "frequency",
      text: "Frequency",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
      formatter: (cell) => `${parseFloat(cell).toFixed(2)} [Mhz]`,
    },
    {
      dataField: "filterbankNchan",
      text: "Nchan",
      sort: true,
      screenSizes: ["xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "filterbankNbit",
      text: "Nbit",
      sort: true,
      screenSizes: ["xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "nantEff",
      text: "Nant Eff",
      sort: true,
      screenSizes: ["xl", "xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "filterbankNpol",
      text: "Npol",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "filterbankDm",
      text: "DM",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
    },
    {
      dataField: "filterbankTsamp",
      text: "tSamp",
      sort: true,
      screenSizes: ["xxl"],
      align: "right",
      headerAlign: "right",
      formatter: (cell) => `${cell} [μs]`,
    },
    {
      dataField: "action",
      text: "",
      align: "right",
      headerAlign: "right",
      sort: false,
      csvExport: false,
    },
  ];

  const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

  const handleProjectFilter = (project) => {
    if (project === "All") {
      setRows(allRows);
      return;
    }

    const newRows = allRows.filter(
      (row) => row.project.short.toLowerCase() === project.toLowerCase()
    );
    setRows(newRows);
  };

  const summaryNode = relayData.observationSummary.edges[0]?.node;
  const summaryData = [
    {
      title: "Observations",
      value: summaryNode.observations,
    },
    {
      title: "Projects",
      value: summaryNode.projects,
    },
    {
      title: "Timespan",
      value: summaryNode.timespanDays,
    },
  ];

  return (
    <div className="search-detail">
      <DataView
        summaryData={summaryData}
        columns={columnsSizeFiltered}
        rows={rows}
        setProject={handleProjectFilter}
        keyField="key"
        card={SearchmodeDetailCard}
      />
    </div>
  );
};

export default SearchDetailTable;
