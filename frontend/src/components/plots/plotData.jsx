import { handleSearch } from "../../helpers";
import moment from "moment";

export const snrPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;

  // Process the table data in a way that react-vis understands.
  const lBandData = results
    .filter((row) => row.observation.band === "LBAND")
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.sn,
      size:  row.observation.duration,
      link:  row.plotLink,
    }));

  const UHFData = results
    .filter((row) => row.observation.band === "UHF")
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.sn,
      size:  row.observation.duration,
      link:  row.plotLink,
    }));

  return { lBandData, UHFData };
};

export const fluxPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;

  const ticks = Array.from(
    new Set(results.map((row) => moment(row.utc.slice(0, 4), "YYYY").valueOf()))
  );

  // Process the table data in a way that react-vis understands.
  const lBandData = results
    .filter((row) => row.observation.band === "LBAND")
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.flux,
      size:  row.observation.duration,
      link:  row.plotLink,
    }));

  const UHFData = results
    .filter((row) => row.band === "UHF")
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.flux,
      size:  row.observation.duration,
      link:  row.plotLink,
    }));

  return { lBandData, UHFData, ticks };
};
