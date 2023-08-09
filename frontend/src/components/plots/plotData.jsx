import { handleSearch } from "../../helpers";
import moment from "moment";

export const snrPlotData = (data, columns, search, residuals) => {
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

export const dmPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;
  console.log(data)
  // Process the table data in a way that react-vis understands.
  const lBandData = results
    .filter((row) => row.observation.band === "LBAND")
    .filter((row) => row.pipelineRun.dm != null)
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.dm,
      error: row.pipelineRun.dmErr,
      size:  row.observation.duration,
      link:  row.plotLink,
    }));

  const UHFData = results
    .filter((row) => row.band === "UHF")
    .filter((row) => row.pipelineRun.dm != null)
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.dm,
      error: row.pipelineRun.dmErr,
      size:  row.observation.duration,
      link:  row.plotLink,
    }));

    const minValue = Math.min(
      ...lBandData.map((entry) => entry.value),
      ...UHFData.map(  (entry) => entry.value)
    );

    const maxValue = Math.max(
      ...lBandData.map((entry) => entry.value),
      ...UHFData.map(  (entry) => entry.value)
    );

  return { lBandData, UHFData, minValue, maxValue };
};

export const rmPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;
  // Process the table data in a way that react-vis understands.
  const lBandData = results
    .filter((row) => row.observation.band === "LBAND")
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.rm,
      error: row.pipelineRun.rmErr,
      size:  row.observation.duration,
      link:  row.plotLink,
    }));

  const UHFData = results
    .filter((row) => row.band === "UHF")
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.rm,
      error: row.pipelineRun.rmErr,
      size:  row.observation.duration,
      link:  row.plotLink,
    }));

    const minValue = Math.min(
      ...lBandData.map((entry) => entry.value),
      ...UHFData.map(  (entry) => entry.value)
    );

    const maxValue = Math.max(
      ...lBandData.map((entry) => entry.value),
      ...UHFData.map(  (entry) => entry.value)
    );

  return { lBandData, UHFData, minValue, maxValue };
};

export const residualPlotData = (residual, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(residual, columns, search)
    : residual;
  console.log(results)
  // Process the table data in a way that react-vis understands.
  const lBandData = results
    .filter((row) => row.toa.pipelineRun.observation.band === "LBAND")
    .map((row) => ({
      time:  row.mjd,
      value: row.residualSec,
      error: row.residualSecErr,
      size:  row.toa.pipelineRun.observation.duration,
      link:  row.plotLink,
    }));

  const UHFData = results
    .filter((row) => row.band === "UHF")
    .map((row) => ({
      time:  row.mjd,
      value: row.residualSec,
      error: row.residualSecErr,
      size:  row.toa.pipelineRun.observation.duration,
      link:  row.plotLink,
    }));

    const minValue = Math.min(
      ...lBandData.map((entry) => entry.value),
      ...UHFData.map(  (entry) => entry.value)
    );

    const maxValue = Math.max(
      ...lBandData.map((entry) => entry.value),
      ...UHFData.map(  (entry) => entry.value)
    );

  return { lBandData, UHFData, minValue, maxValue };
};
