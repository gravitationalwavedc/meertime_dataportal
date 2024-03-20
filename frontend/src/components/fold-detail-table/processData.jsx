import { createColumnHelper } from "@tanstack/react-table";
import { formatUTC } from "../../helpers";
import TableButtons from "./TableButtons";

export function getColumns() {
  const columnHelper = createColumnHelper();

  return [
    columnHelper.accessor("Timestamp"),
    columnHelper.accessor("Project"),
    columnHelper.accessor("Length", {
      cell: (info) => `${info.getValue()} [s]`,
    }),
    columnHelper.accessor("Beam"),
    columnHelper.accessor("Nchan"),
    columnHelper.accessor("BW"),
    columnHelper.accessor("Band"),
    columnHelper.accessor("Nbin"),
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
    viewLink: `/${mainProject}/${jname}/${formatUTC(
      node.observation.utcStart
    )}/${node.observation.beam}/`,
    sessionLink: `/session/${node.observation.calibration.idInt}/`,
    embargoEndDate: node.observation.embargoEndDate,
    restricted: node.observation.restricted,
  }));
}
