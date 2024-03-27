import { createColumnHelper } from "@tanstack/react-table";
import { formatUTC } from "../../helpers";
import TableButtons from "./TableButtons";

export function getColumns() {
  const columnHelper = createColumnHelper();

  return [
    columnHelper.accessor("Timestamp", {
      header: "Timestamp",
      enableHiding: false,
    }),
    columnHelper.accessor("Project", {
      header: "Project",
      enableHiding: false,
    }),
    columnHelper.accessor("Badges", {
      header: "Badges",
      enableHiding: false,
    }),
    columnHelper.accessor("Length", {
      header: "Length",
      cell: (info) => `${info.getValue()} [s]`,
    }),
    columnHelper.accessor("Beam", {
      header: "Beam",
      enableHiding: false,
    }),
    columnHelper.accessor("Nchan", {
      header: "Nchan",
    }),
    columnHelper.accessor("BW", {
      header: "Band width",
    }),
    columnHelper.accessor("Band", {
      header: "Band",
    }),
    columnHelper.accessor("Nbin", {
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
    columnHelper.display({
      id: "actions",
      cell: (props) => <TableButtons row={props.row} />,
      canSort: false,
      enableHiding: false,
    }),
  ];
}

function formatNumber(value, decimals) {
  return value ? value.toFixed(decimals) : "null";
}

export function processData(fragmentData, mainProject, jname) {
  return fragmentData.pulsarFoldResult.edges.map(({ node }) => ({
    Timestamp: formatUTC(node.observation.utcStart),
    Project: node.observation.project.short,
    Length: formatNumber(node.observation.duration, 2),
    Beam: node.observation.beam,
    BW: node.observation.bandwidth,
    Nchan: node.observation.nchan,
    Band: node.observation.band,
    Nbin: node.observation.foldNbin,
    nantEff: node.observation.nantEff,
    dmBackend: formatNumber(node.observation.ephemeris.dm, 2),
    dmFit: formatNumber(node.pipelineRun.dm, 1),
    rm: formatNumber(node.pipelineRun.rm, 1),
    sn: formatNumber(node.pipelineRun.sn, 1),
    Badges: node.observation.badges.edges.map(({ node }) => ({
      name: node.name,
      description: node.description,
    })),
    viewLink: `/${mainProject}/${jname}/${formatUTC(
      node.observation.utcStart
    )}/${node.observation.beam}/`,
    sessionLink: `/session/${node.observation.calibration.idInt}/`,
    embargoEndDate: node.observation.embargoEndDate,
    restricted: node.observation.restricted,
  }));
}
