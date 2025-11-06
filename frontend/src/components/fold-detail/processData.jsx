import { createColumnHelper } from "@tanstack/react-table";
import { formatUTC } from "../../helpers";
import TableButtons from "./TableButtons";

export function getColumns() {
  const columnHelper = createColumnHelper();

  return [
    columnHelper.accessor("timestamp", {
      header: "Timestamp",
      enableHiding: false,
    }),
    columnHelper.accessor("project", {
      header: "Project",
      enableHiding: false,
    }),
    columnHelper.accessor("length", {
      header: "Length",
      cell: (info) => `${info.getValue()} [s]`,
    }),
    columnHelper.accessor("beam", {
      header: "Beam",
      enableHiding: false,
    }),
    columnHelper.accessor("nchan", {
      header: "Nchan",
    }),
    columnHelper.accessor("bw", {
      header: "Band width",
    }),
    columnHelper.accessor("band", {
      header: "Band",
    }),
    columnHelper.accessor("nbin", {
      header: "Nbin",
    }),
    columnHelper.accessor("nantEff", {
      header: "Nant Eff",
    }),
    columnHelper.accessor("dmBackend", {
      header: "DM Backend",
    }),
    columnHelper.accessor("dmFit", {
      header: "DM Fit",
    }),
    columnHelper.accessor("rm", {
      header: "RM",
    }),
    columnHelper.accessor("sn", {
      header: "S/N",
    }),
    columnHelper.accessor("flux", {
      header: "Flux",
      cell: (info) =>
        info.getValue() === null ? "null" : `${info.getValue()} [mJy]`,
    }),
    columnHelper.display({
      id: "actions",
      header: null,
      cell: (props) => <TableButtons row={props.row} />,
      canSort: false,
      enableHiding: false,
    }),
  ];
}

function formatNumber(value, decimals) {
  return value ? value.toFixed(decimals) : "null";
}

export function processData(data, mainProject, jname) {
  return data.pulsarFoldResult.edges.map(({ node }) => ({
    timestamp: formatUTC(node.observation.utcStart),
    project: node.observation.project.short,
    length: formatNumber(node.observation.duration, 2),
    beam: node.observation.beam,
    bw: node.observation.bandwidth,
    nchan: node.observation.nchan,
    band: node.observation.band,
    nbin: node.observation.foldNbin,
    flux: node.pipelineRun.flux,
    nantEff: node.observation.nantEff,
    dmBackend: formatNumber(node.observation.ephemeris.dm, 2),
    dmFit: formatNumber(node.pipelineRun.dm, 2),
    rm: formatNumber(node.pipelineRun.rm, 1),
    sn: formatNumber(node.pipelineRun.sn, 1),
    badges: node.pipelineRun.badges.edges
      .map(({ node }) => ({
        name: node.name,
        description: node.description,
      }))
      .concat(
        node.pipelineRun.observation.calibration.badges.edges.map(
          ({ node }) => ({
            name: node.name,
            description: node.description,
          })
        )
      )
      .concat(
        node.observation.badges.edges.map(({ node }) => ({
          name: node.name,
          description: node.description,
        }))
      ),
    viewLink: `/${mainProject}/${jname}/${formatUTC(
      node.observation.utcStart
    )}/${node.observation.beam}/`,
    sessionLink: `/session/${node.observation.calibration.idInt}/`,
    embargoEndDate: node.observation.embargoEndDate,
    restricted: node.observation.restricted,
  }));
}
