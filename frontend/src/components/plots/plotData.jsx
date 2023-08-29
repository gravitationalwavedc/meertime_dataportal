import { handleSearch, mjdToUnixTimestamp } from "../../helpers";
import moment from "moment";

export const formatYAxisTick = (value) => {
  return value.toFixed(2);
};

export const filterBandData = (data) => {
  data = data.filter((row) => row.value !== null);

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
      .map((row) => row.value)
  );

  const maxValue = Math.max(
    ...data
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
  const allData = results
    .map((row) => ({
      utc:   moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      day:   row.observation.dayOfYear,
      phase: row.observation.binaryOrbitalPhase,
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
      utc:   moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      day:   row.observation.dayOfYear,
      phase: row.observation.binaryOrbitalPhase,
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
  // Process the table data in a way that react-vis understands.
  const allData = results
    .map((row) => ({
      utc:   moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      day:   row.observation.dayOfYear,
      phase: row.observation.binaryOrbitalPhase,
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
      utc:   moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
      day:   row.observation.dayOfYear,
      phase: row.observation.binaryOrbitalPhase,
      value: row.pipelineRun.rm,
      error: row.pipelineRun.rmErr,
      size:  row.observation.duration,
      link:  row.plotLink,
      band:  row.observation.band,
    }));

    return filterBandData(allData);
};

export const residualPlotData = (data, columns, search) => {
  // Pass table data through the search filter to enable searching pulsars on chart.
  const results = search.searchText
    ? handleSearch(residual, columns, search)
    : data;

  const run_toas = results.reduce( (result_returned, run_result) => {
    // Run for each pipelineRun
    const run_results = run_result.pipelineRun.toas.edges.reduce( (result, edge) => {
      // Grab all of the info needed from the toa
      if (edge.node.residual) {
        result.push({
          mjd:                edge.node.residual.mjd,
          dayOfYear:          edge.node.residual.dayOfYear,
          binaryOrbitalPhase: edge.node.residual.binaryOrbitalPhase,
          residualSec:        edge.node.residual.residualSec,
          residualSecErr:     edge.node.residual.residualSecErr,
          duration:           edge.node.length,
          plotLink:           run_result.plotLink,
          band:               run_result.observation.band,
        });
        return result;
      }
      else {
        // No residuals for this run so return nothing
        return [];
      }
    }, []);
    result_returned.push(run_results);
    return result_returned;
  }, []);
  // Combine the array of arrays
  const toas = [].concat(...run_toas);

  const allData = toas
    .map((row) => ({
      utc:   moment(mjdToUnixTimestamp(row.mjd)).valueOf(),
      day:   row.dayOfYear,
      phase: row.binaryOrbitalPhase,
      value: row.residualSec   * 1e6,
      error: row.residualSecErr* 1e9,
      size:  row.duration,
      link:  row.plotLink,
      band:  row.band,
    }));
    console.log("toas:", allData);

    return filterBandData(allData);
};
