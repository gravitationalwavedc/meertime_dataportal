import { useState } from "react";
import { Col, Table } from "react-bootstrap";
import { graphql, useFragment } from "react-relay";
import { getColumns, processData } from "./processData";
import { Form } from "react-bootstrap";
import DebouncedInput from "../form-inputs/DebouncedInput";

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getFacetedUniqueValues,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";

const TanTableTestFragment = graphql`
  fragment TanTableTestFragment on Query
  @argumentDefinitions(
    pulsar: { type: "String" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
  ) {
    observationSummary(
      pulsar_Name: $pulsar
      obsType: "fold"
      calibration_Id: "All"
      mainProject: $mainProject
      project_Short: "All"
      band: "All"
    ) {
      edges {
        node {
          observations
          observationHours
          projects
          pulsars
          estimatedDiskSpaceGb
          timespanDays
          maxDuration
          minDuration
        }
      }
    }
    pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
      residualEphemeris {
        ephemerisData
        createdAt
      }
      description
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
          }
        }
      }
    }
  }
`;

const TanTableTest = ({ tableData, mainProject, jname }) => {
  const fragmentData = useFragment(TanTableTestFragment, tableData);
  const [data] = useState(processData(fragmentData, mainProject, jname));
  const [globalFilter, setGlobalFilter] = useState("");

  const columns = getColumns();

  const table = useReactTable({
    data,
    columns,
    state: {
      globalFilter,
    },
    initialState: {
      sorting: [
        {
          id: "Timestamp",
          desc: true,
        },
      ],
    },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
  });

  const infoHeaders = ["Timestamp", "Project", "Beam"];

  console.log(table.getRowModel().rows);

  return (
    <div className="p-2">
      <Form.Row>
        <Col md={3} xl={2}>
          <Form.Group controlId="projectSelect">
            <Form.Label>Project</Form.Label>
            <Form.Control
              custom
              role="project-select"
              as="select"
              onChange={(event) =>
                table.getColumn("Project").setFilterValue(event.target.value)
              }
            >
              <option value="">All</option>
              {[...table.getColumn("Project").getFacetedUniqueValues()].map(
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
                table.getColumn("Band").setFilterValue(event.target.value)
              }
            >
              <option value="">All</option>
              {[...table.getColumn("Band").getFacetedUniqueValues()].map(
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
            <Form.Label>Order by</Form.Label>
            <Form.Control custom role="order-by" as="select">
              {table
                .getHeaderGroups()
                .map((headerGroup) =>
                  headerGroup.headers.map((header) => (
                    <>
                      {header.isPlaceholder ? null : (
                        <option key={header.id}>
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                        </option>
                      )}
                    </>
                  ))
                )}
            </Form.Control>
          </Form.Group>
        </Col>
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
      </Form.Row>
      <Table className="react-bootstrap-table">
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              <td>
                <Col>
                  <span className="text-primary-800 bold pr-2">
                    {row.original.Timestamp}
                  </span>{" "}
                  {row.original.Project} &#183; {row.original.Beam} beam
                </Col>
                <Col>Badge, badge, badge, badge</Col>
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
      <div className="h-4" />
    </div>
  );
};

export default TanTableTest;
