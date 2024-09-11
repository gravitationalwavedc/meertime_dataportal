import { useState } from "react";
import { HiDownload } from "react-icons/hi";
import { Badge, Button, Col, Row, Table } from "react-bootstrap";
import { graphql, useFragment } from "react-relay";
import { getColumns, processData } from "./processData";
import { Form } from "react-bootstrap";
import DebouncedInput from "../form-inputs/DebouncedInput";
import {
  HiOutlineSortAscending,
  HiOutlineSortDescending,
} from "react-icons/hi";
import { generateCsv, mkConfig, download } from "export-to-csv";

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getFacetedUniqueValues,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import ColumnToggle from "../form-inputs/ColumnToggle";

const FoldDetailTableFragment = graphql`
  fragment FoldDetailTableFragment on Query
  @refetchable(queryName: "FoldDetailTableRefetchQuery")
  @argumentDefinitions(
    pulsar: { type: "String" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
    excludeBadges: { type: "[String]", defaultValue: [] }
    minimumSNR: { type: "Float", defaultValue: 8 }
  ) {
    pulsarFoldResult(
      pulsar: $pulsar
      mainProject: $mainProject
      excludeBadges: $excludeBadges
      minimumSNR: $minimumSNR
    ) {
      edges {
        node {
          observation {
            id
            utcStart
            dayOfYear
            binaryOrbitalPhase
            duration
            beam
            bandwidth
            nchan
            band
            foldNbin
            nant
            nantEff
            restricted
            embargoEndDate
            project {
              short
            }
            ephemeris {
              dm
            }
            calibration {
              idInt
            }
          }
          pipelineRun {
            dm
            dmErr
            rm
            rmErr
            sn
            flux
            badges {
              edges {
                node {
                  name
                  description
                }
              }
            }
            observation {
              calibration {
                badges {
                  edges {
                    node {
                      name
                      description
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
`;

const FoldDetailTable = ({ tableData, mainProject, jname }) => {
  const fragmentData = useFragment(FoldDetailTableFragment, tableData);
  const [data] = useState(processData(fragmentData, mainProject, jname));
  const [globalFilter, setGlobalFilter] = useState("");
  const [sorting, setSorting] = useState([{ id: "timestamp", desc: true }]);

  const columns = getColumns();

  const table = useReactTable({
    data,
    columns,
    state: {
      globalFilter,
      sorting,
    },
    initialState: {
      columnVisibility: {
        dmFit: mainProject !== "MONSPSR",
        rm: mainProject !== "MONSPSR",
        nant: mainProject !== "MONSPSR",
        nantEff: mainProject !== "MONSPSR",
        band: mainProject !== "MONSPSR",
        dmBackend: mainProject !== "MONSPSR",
      },
    },
    onGlobalFilterChange: setGlobalFilter,
    onSortChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
  });

  const handleExportCSV = () => {
    const csvConfig = mkConfig({
      fieldSeparator: ",",
      decimalSeparator: ".",
      useKeysAsHeaders: true,
      filename: `${mainProject}_${jname}_observations`,
    });

    const data = table.getRowModel().rows.map((row) =>
      row
        .getVisibleCells()
        .filter((cell) => cell.column.id !== "actions")
        .reduce(
          (acc, cell) => ({ ...acc, [cell.column.id]: cell.getValue() }),
          {}
        )
    );

    const csv = generateCsv(csvConfig)(data);
    download(csvConfig)(csv);
  };

  // These columns are displayed as information in the first column
  const infoHeaders = ["timestamp", "project", "beam", "badges"];

  return (
    <>
      <Row className="pt-5 pb-4">
        <Col>
          <h4 className="text-primary-600">Observations</h4>
        </Col>
      </Row>
      <Form.Row className="searchbar">
        <Col md={3} xl={2}>
          <Form.Group controlId="projectSelect">
            <Form.Label>Project</Form.Label>
            <Form.Control
              custom
              role="project-select"
              as="select"
              onChange={(event) =>
                table.getColumn("project").setFilterValue(event.target.value)
              }
            >
              <option value="">All</option>
              {[...table.getColumn("project").getFacetedUniqueValues()].map(
                ([key]) => (
                  <option value={key} key={key}>
                    {key}
                  </option>
                )
              )}
            </Form.Control>
          </Form.Group>
        </Col>
        <Col md={3} xl={2}>
          <Form.Group controlId="projectSelect">
            <Form.Label>Band</Form.Label>
            <Form.Control
              custom
              role="project-select"
              as="select"
              onChange={(event) =>
                table.getColumn("band").setFilterValue(event.target.value)
              }
            >
              <option value="">All</option>
              {[...table.getColumn("band").getFacetedUniqueValues()].map(
                ([key]) => (
                  <option value={key} key={key}>
                    {key}
                  </option>
                )
              )}
            </Form.Control>
          </Form.Group>
        </Col>
        <Col md={3} xl={2}>
          <Form.Group controlId="sortSelect">
            <Form.Label>Order by</Form.Label>
            <Form.Control
              custom
              role="order-by"
              as="select"
              onChange={(event) =>
                setSorting([{ id: event.target.value, desc: true }])
              }
            >
              {table.getHeaderGroups().map((headerGroup) =>
                headerGroup.headers
                  .filter((header) => header.column.getCanSort())
                  .map((header) => (
                    <option key={header.id} value={header.id}>
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                    </option>
                  ))
              )}
            </Form.Control>
          </Form.Group>
        </Col>
        <Form.Group>
          <Button
            variant="link"
            size="sm"
            onClick={() =>
              setSorting((prev) =>
                prev.map((sortState) => ({
                  id: sortState.id,
                  desc: !sortState.desc,
                }))
              )
            }
          >
            {sorting[0].desc ? (
              <>
                <HiOutlineSortDescending className="icon" />
                Descending
              </>
            ) : (
              <>
                <HiOutlineSortAscending className="icon" />
                Ascending
              </>
            )}
          </Button>
        </Form.Group>
      </Form.Row>
      <Form.Row className="searchbar">
        <Col md={4} xl={3}>
          <Form.Group controlId="search">
            <Form.Label>Search</Form.Label>
            <DebouncedInput
              value={globalFilter ?? ""}
              onChange={(value) => setGlobalFilter(String(value))}
              placeholder="Search observations..."
              className="form-control"
            />
          </Form.Group>
        </Col>
        <Form.Group>
          <ColumnToggle table={table} />
        </Form.Group>
        <Form.Group>
          <Button
            className="mr-2 ml-2"
            variant="link"
            size="sm"
            onClick={() => handleExportCSV()}
          >
            <HiDownload className="icon" />
            Download CSV
          </Button>
        </Form.Group>
      </Form.Row>
      <Table responsive className="react-bootstrap-table mt-1">
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              <td>
                <Col>
                  <span className="h6 text-primary-600 bold pr-2">
                    {row.original.timestamp}
                  </span>{" "}
                  {row.original.project} &#183; {row.original.beam} beam
                </Col>
                <Col>
                  {row.original.badges.map((badge) => (
                    <Badge key={badge.name} variant="primary" className="mr-1">
                      {badge.name}
                    </Badge>
                  ))}
                </Col>
              </td>
              {row
                .getVisibleCells()
                .filter(
                  (cell) => !infoHeaders.includes(cell.column.columnDef.header)
                )
                .map((cell) => (
                  <td key={cell.id}>
                    <Col className="overline">
                      {cell.column.columnDef.header}
                    </Col>
                    <Col>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </Col>
                  </td>
                ))}
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
};

export default FoldDetailTable;
