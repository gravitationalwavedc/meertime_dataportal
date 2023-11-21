import { mjdToUnixTimestamp } from "../../helpers";
import moment from "moment";

export const formatYAxisTick = (value) => {
  return value.toFixed(2);
};

export const getXaxisFormatter = (xAxis) => {
  if (xAxis === "utc") {
    return (unixTime) => moment(unixTime).format("YYYY");
  } else if (xAxis === "day") {
    return formatYAxisTick;
  } else if (xAxis === "phase") {
    return formatYAxisTick;
  } else {
    return (unixTime) => moment(unixTime).format("YYYY");
  }
};

export const getXaxisLabel = (xAxis) => {
  if (xAxis === "utc") {
    return "UTC";
  } else if (xAxis === "day") {
    return "Day of the year";
  } else if (xAxis === "phase") {
    return "Binary orbit phase";
  } else {
    return "UTC";
  }
};

export const getYaxisLabel = (yAxis) => {
  if (yAxis === "S/N") {
    return "S/N";
  } else if (yAxis === "Flux Density") {
    return "Flux Density (mJy)";
  } else if (yAxis === "DM") {
    return "Fit DM (pc cm^-3)";
  } else if (yAxis === "RM") {
    return "Fit RM (rad m^-2)";
  } else if (yAxis === "Residual") {
    return "Residual (μs)";
  }
};

export const getZRange = (yAxis) => {
  if (yAxis === "S/N") {
    return [40, 400];
  } else if (yAxis === "Flux Density") {
    return [40, 400];
  } else if (yAxis === "DM") {
    return [40, 400];
  } else if (yAxis === "RM") {
    return [40, 400]
  } else if (yAxis === "Residual") {
    return [20, 300];
  }
};


export const toolTipFormatter = (value, name) => {
  if (name === "UTC") {
    return [moment(value).format("DD-MM-YYYY-hh:mm:ss"), name];
  }

  if (name === "Size") {
    return [`${value} [m]`, "Integration time"];
  }

  return [value, name];
};

export const getActivePlotData = (data, activePlot, zoomArea) => {
  const plotFunctions = {
    "S/N": snrPlotData,
    "Flux Density": fluxPlotData,
    "DM": dmPlotData,
    "RM": rmPlotData,
    "Residual": residualPlotData,
  };
  const plotFunction = plotFunctions[activePlot];
  if (plotFunction) {
    const { plotData, minValue, maxValue, ticks } = plotFunction(data, zoomArea);
    return { plotData, minValue, maxValue, ticks };
  } else {
    // Handle the case when activePlot is not recognized
    console.error(`Unknown activePlot: ${activePlot}`);
    // You might want to return default values or throw an error, depending on your use case
    return { plotData: [], minValue: 0, maxValue: 0, ticks: [] };
  }
}

export const filterBandData = (data, zoomArea) => {
  data = data.filter((row) => row.value !== null);

  const { xMin, xMax, yMin, yMax } = zoomArea;
  if (xMin != null && xMax != null && yMin != null && yMax != null) {
    data = data.filter(
      (dataPoint) =>
        dataPoint.value >= yMin && dataPoint.value <= yMax &&
        ((dataPoint.time >= xMin && dataPoint.time <= xMax) ||
          (dataPoint.utc >= xMin && dataPoint.utc <= xMax) ||
          (dataPoint.date >= xMin && dataPoint.date <= xMax) ||
          (dataPoint.phase >= xMin && dataPoint.phase <= xMax))
    );
  }
  // Process the table data in a way that react-vis understands.
  const UHFData = data.filter((row) => row.band === "UHF");
  const UHF = {
    data: UHFData,
    name: "UHF",
    colour: "#0d0887",
    shape: "square",
  };

  const lBandData = data.filter((row) => row.band === "LBAND");
  const lBand = {
    data: lBandData,
    name: "LBAND",
    colour: "#6001a6",
    shape: "circle",
  };

  const sband0Data = data.filter((row) => row.band === "SBAND_0");
  const sband0 = {
    data: sband0Data,
    name: "SBAND_0",
    colour: "#cd4a76",
    shape: "triangle",
  };

  const sband1Data = data.filter((row) => row.band === "SBAND_1");
  const sband1 = {
    data: sband1Data,
    name: "SBAND_1",
    colour: "#df6263",
    shape: "triangle",
  };

  const sband2Data = data.filter((row) => row.band === "SBAND_2");
  const sband2 = {
    data: sband2Data,
    name: "SBAND_2",
    colour: "#ee7b51",
    shape: "triangle",
  };

  const sband3Data = data.filter((row) => row.band === "SBAND_3");
  const sband3 = {
    data: sband3Data,
    name: "SBAND_3",
    colour: "#f9973f",
    shape: "triangle",
  };

  const sband4Data = data.filter((row) => row.band === "SBAND_4");
  const sband4 = {
    data: sband4Data,
    name: "SBAND_4",
    colour: "#fdb52e",
    shape: "triangle",
  };

  const minValue = Math.min(...data.map((row) => row.value));

  const maxValue = Math.max(...data.map((row) => row.value));

  const unsortedTicks = Array.from(
    new Set(data.map((row) => moment(moment(row.utc).format("YYYY")).valueOf()))
  );
  const ticks = unsortedTicks.sort((a, b) => a - b);

  const plotData = [lBand, UHF, sband0, sband1, sband2, sband3, sband4];

  return { plotData, minValue, maxValue, ticks };
};

export const snrPlotData = (data, zoomArea) => {
  // Process the table data in a way that react-vis understands.
  const allData = data.map((row) => ({
    utc: moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: row.observation.dayOfYear,
    phase: row.observation.binaryOrbitalPhase,
    value: row.pipelineRun.sn,
    size: row.observation.duration,
    link: row.plotLink,
    band: row.observation.band,
  }));

  return filterBandData(allData, zoomArea);
};

export const fluxPlotData = (data, zoomArea) => {
  const allData = data.map((row) => ({
    utc: moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: row.observation.dayOfYear,
    phase: row.observation.binaryOrbitalPhase,
    value: row.pipelineRun.flux,
    size: row.observation.duration,
    link: row.plotLink,
    band: row.observation.band,
  }));

  return filterBandData(allData, zoomArea);
};

export const dmPlotData = (data, zoomArea) => {
  // Process the table data in a way that react-vis understands.
  const allData = data.map((row) => ({
    utc: moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: row.observation.dayOfYear,
    phase: row.observation.binaryOrbitalPhase,
    value: row.pipelineRun.dm,
    error: row.pipelineRun.dmErr,
    size: row.observation.duration,
    link: row.plotLink,
    band: row.observation.band,
  }));

  return filterBandData(allData, zoomArea);
};

export const rmPlotData = (data, zoomArea) => {
  // Process the table data in a way that react-vis understands.
  const allData = data.map((row) => ({
    utc: moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: row.observation.dayOfYear,
    phase: row.observation.binaryOrbitalPhase,
    value: row.pipelineRun.rm,
    error: row.pipelineRun.rmErr,
    size: row.observation.duration,
    link: row.plotLink,
    band: row.observation.band,
  }));

  return filterBandData(allData, zoomArea);
};

export const residualPlotData = (data, zoomArea) => {
  const run_toas = data.reduce((result_returned, run_result) => {
    // Run for each pipelineRun
    const run_results = run_result.pipelineRun.toas.edges.reduce(
      (result, edge) => {
        // Grab all of the info needed from the toa
        if (edge.node.residual) {
          result.push({
            mjd: edge.node.residual.mjd,
            dayOfYear: edge.node.residual.dayOfYear,
            binaryOrbitalPhase: edge.node.residual.binaryOrbitalPhase,
            residualSec: edge.node.residual.residualSec,
            residualSecErr: edge.node.residual.residualSecErr,
            duration: edge.node.length,
            plotLink: run_result.plotLink,
            band: run_result.observation.band,
          });
          return result;
        } else {
          // No residuals for this run so return nothing
          return [];
        }
      },
      []
    );
    result_returned.push(run_results);
    return result_returned;
  }, []);
  // Combine the array of arrays
  const toas = [].concat(...run_toas);

  const allData = toas.map((row) => ({
    utc: moment(mjdToUnixTimestamp(row.mjd)).valueOf(),
    day: row.dayOfYear,
    phase: row.binaryOrbitalPhase,
    value: row.residualSec * 1e6,
    error: row.residualSecErr * 1e9,
    size: row.duration,
    link: row.plotLink,
    band: row.band,
  }));

  return filterBandData(allData, zoomArea);
};
