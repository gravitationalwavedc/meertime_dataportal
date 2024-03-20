import { useState } from "react";
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

  console.log(table.getState().sorting);

  return (
    <div className="p-2">
      <DebouncedInput
        value={globalFilter ?? ""}
        onChange={(value) => setGlobalFilter(String(value))}
        placeholder="Search observations"
      />
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
      <table>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                >
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="h-4" />
    </div>
  );
};

export default TanTableTest;
