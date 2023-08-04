import { handleSearch } from "../../helpers";
import moment from "moment";

export const filterBandData = (data) => {
  console.log(data);

  // Process the table data in a way that react-vis understands.
  const lBandData = data
    .filter((row) => row.band === "LBAND");
  const lBand = {
    data:   lBandData,
    name:   "LBAND",
    colour: "#440154", // #8884d8
    shape:  "circle",
  };

  const UHFData = data
    .filter((row) => row.band === "UHF");
  const UHF = {
    data:   UHFData,
    name:   "UHF",
    colour: "#3e4a89", // #e07761
    shape:  "square",
  };

  const sband0Data = data
    .filter((row) => row.band === "SBAND_0");
  const sband0 = {
    data:   sband0Data,
    name:   "SBAND_0",
    colour: "#31688e",
    shape:  "triangle",
  };

  const sband1Data = data
    .filter((row) => row.band === "SBAND_1");
  const sband1 = {
    data:   sband1Data,
    name:   "SBAND_1",
    colour: "#26828e",
    shape:  "triangle",
  };

  const sband2Data = data
    .filter((row) => row.band === "SBAND_2");
  const sband2 = {
    data:   sband2Data,
    name:   "SBAND_2",
    colour: "#1f9e89",
    shape:  "triangle",
  };

  const sband3Data = data
    .filter((row) => row.band === "SBAND_3");
  const sband3 = {
    data:   sband3Data,
    name:   "SBAND_3",
    colour: "#35b779",
    shape:  "triangle",
  };

  const sband4Data = data
    .filter((row) => row.band === "SBAND_4");
  const sband4 = {
    data:   sband4Data,
    name:   "SBAND_4",
    colour: "#6ece58",
    shape:  "triangle",
  };

  const minValue = Math.min(
    ...data
      .filter((row) => row.value !== null)
      .map((row) => row.value)
  );

  const maxValue = Math.max(
    ...data
      .filter((row) => row.value !== null)
      .map((row) => row.value)
  );

  const ticks = Array.from(
    new Set(data.map((row) => moment(row.utc.slice(0, 4), "YYYY").valueOf()))
  );

  const plotData = [ lBand, UHF, sband0, sband1, sband2, sband3, sband4 ];

  return { plotData, minValue, maxValue, ticks };
};


export const snrPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;

  // Process the table data in a way that react-vis understands.
  console.log(results);
  const allData = results
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.sn,
      size:  row.observation.duration,
      link:  row.plotLink,
      band:  row.observation.band,
    }));

    return filterBandData(allData);
};

export const fluxPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;

  const allData = results
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.flux,
      size:  row.observation.duration,
      link:  row.plotLink,
      band:  row.observation.band,
    }));

    return filterBandData(allData);
};

export const dmPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;
  console.log(data)
  // Process the table data in a way that react-vis understands.
  const allData = results
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.dm,
      error: row.pipelineRun.dmErr,
      size:  row.observation.duration,
      link:  row.plotLink,
      band:  row.observation.band,
    }));

    return filterBandData(allData);
};

export const rmPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;
  // Process the table data in a way that react-vis understands.
  const allData = results
    .map((row) => ({
      time:  moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      value: row.pipelineRun.rm,
      error: row.pipelineRun.rmErr,
      size:  row.observation.duration,
      link:  row.plotLink,
      band:  row.observation.band,
    }));

    return filterBandData(allData);
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
