import { calculateMedian, mjdToUnixTimestamp } from "../../helpers";
import moment from "moment";

export const getXaxisFormatter = (xAxis) => {
  if (xAxis === "utc") {
    return {
      title: {
        text: getXaxisLabel(xAxis),
      },
      type: 'date',
      tickformat: '%Y'
    };
  } else if (xAxis === "day") {
    return {
      title: {
        text: getXaxisLabel(xAxis),
      },
    };
  } else if (xAxis === "phase") {
    return {
      title: {
        text: getXaxisLabel(xAxis),
      },
    };
  } else {
    return {
      title: {
        text: getXaxisLabel(xAxis),
      },
      type: 'date',
      tickformat: '%Y'
    };
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

export const getYaxisDomain = (yAxis, minValue, maxValue, medianValue) => {
  if (yAxis === "S/N") {
    return [0, maxValue];
  } else if (yAxis === "Flux Density") {
    return [minValue, maxValue];
  } else if (yAxis === "DM" || yAxis === "RM") {
    const absDiff = Math.max(
      Math.abs(minValue - medianValue),
      Math.abs(maxValue - medianValue)
    );
    return [medianValue - absDiff, medianValue + absDiff];
  } else if (yAxis === "Residual") {
    const absMax = Math.max(Math.abs(minValue), Math.abs(maxValue));
    return [-absMax, absMax];
  }
};

export const getYaxisTicks = (yAxis, minValue, maxValue, medianValue) => {
  if (yAxis === "S/N") {
    return [0, maxValue * 0.25, maxValue * 0.5, maxValue * 0.75, maxValue];
  } else if (yAxis === "Flux Density") {
    return null;
  } else if (yAxis === "DM" || yAxis === "RM") {
    const absDiff = Math.max(
      Math.abs(minValue - medianValue),
      Math.abs(maxValue - medianValue)
    );
    return [
      medianValue - absDiff,
      medianValue - absDiff * 0.5,
      medianValue,
      medianValue + absDiff * 0.5,
      medianValue + absDiff,
    ];
  } else if (yAxis === "Residual") {
    const absMax = Math.max(Math.abs(minValue), Math.abs(maxValue));
    return [-absMax, -absMax * 0.5, 0, absMax * 0.5, absMax];
  }
};

export const getActivePlotData = (data, activePlot, timingProject) => {
  console.log("getActivePlotData", data);
  const plotFunctions = {
    "S/N": snrPlotData,
    "Flux Density": fluxPlotData,
    DM: dmPlotData,
    RM: rmPlotData,
    Residual: residualPlotData,
  };
  const plotFunction = plotFunctions[activePlot];
  if (plotFunction) {
    const activePlotData = plotFunction(data, timingProject);
    return activePlotData;
  } else {
    // Handle the case when activePlot is not recognized
    console.error(`Unknown activePlot: ${activePlot}`);
    // You might want to return default values or throw an error, depending on your use case
    return [];
  }
};

export const filterBandData = ( data ) => {
  data = data.filter((row) => row.value !== null);

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
    shape: "triangle-up",
  };

  const sband1Data = data.filter((row) => row.band === "SBAND_1");
  const sband1 = {
    data: sband1Data,
    name: "SBAND_1",
    colour: "#df6263",
    shape: "triangle-up",
  };

  const sband2Data = data.filter((row) => row.band === "SBAND_2");
  const sband2 = {
    data: sband2Data,
    name: "SBAND_2",
    colour: "#ee7b51",
    shape: "triangle-up",
  };

  const sband3Data = data.filter((row) => row.band === "SBAND_3");
  const sband3 = {
    data: sband3Data,
    name: "SBAND_3",
    colour: "#f9973f",
    shape: "triangle-up",
  };

  const sband4Data = data.filter((row) => row.band === "SBAND_4");
  const sband4 = {
    data: sband4Data,
    name: "SBAND_4",
    colour: "#fdb52e",
    shape: "triangle-up",
  };

  const minValue = Math.min(...data.map((row) => row.value - (row.error || 0)));

  const maxValue = Math.max(...data.map((row) => row.value + (row.error || 0)));

  const medianValue = calculateMedian(data);

  const unsortedTicks = Array.from(
    new Set(data.map((row) => moment(moment(row.utc).format("YYYY")).valueOf()))
  );
  const ticks = unsortedTicks.sort((a, b) => a - b);

  const plotData = [lBand, UHF, sband0, sband1, sband2, sband3, sband4];

  return { plotData, minValue, maxValue, medianValue, ticks };
};

export const snrPlotData = (data) => {
  // Process the table data in a way that react-vis understands.
  const allData = data.map((row) => ({
    id: row.observation.id,
    utc: moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: row.observation.dayOfYear,
    phase: row.observation.binaryOrbitalPhase,
    value: row.pipelineRun.sn,
    size: row.observation.duration,
    link: row.plotLink,
    band: row.observation.band,
  }));

  return allData;
};

export const fluxPlotData = (data) => {
  const allData = data.map((row) => ({
    id: row.observation.id,
    utc: moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: row.observation.dayOfYear,
    phase: row.observation.binaryOrbitalPhase,
    value: row.pipelineRun.flux,
    size: row.observation.duration,
    link: row.plotLink,
    band: row.observation.band,
  }));

  return allData;
};

export const dmPlotData = (data) => {
  // Process the table data in a way that react-vis understands.
  const allData = data.map((row) => ({
    id: row.observation.id,
    utc: moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: row.observation.dayOfYear,
    phase: row.observation.binaryOrbitalPhase,
    value: row.pipelineRun.dm,
    error: row.pipelineRun.dmErr,
    size: row.observation.duration,
    link: row.plotLink,
    band: row.observation.band,
  }));

  return allData;
};

export const rmPlotData = (data) => {
  // Process the table data in a way that react-vis understands.
  const allData = data.map((row) => ({
    id: row.observation.id,
    utc: moment(row.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: row.observation.dayOfYear,
    phase: row.observation.binaryOrbitalPhase,
    value: row.pipelineRun.rm,
    error: row.pipelineRun.rmErr,
    size: row.observation.duration,
    link: row.plotLink,
    band: row.observation.band,
  }));

  return allData;
};

export const residualPlotData = (data, timingProject) => {
  const run_toas = data.reduce((result_returned, run_result) => {
    // Run for each pipelineRun
    const run_results = run_result.observation.toas.edges.reduce(
      (result, edge) => {
        // Grab all of the info needed from the toa
        if (edge.node.residual) {
          if (edge.node.project.short === timingProject) {
            result.push({
              id: edge.node.residual.id,
              mjd: edge.node.residual.mjd,
              dayOfYear: edge.node.residual.dayOfYear,
              binaryOrbitalPhase: edge.node.residual.binaryOrbitalPhase,
              residualSec: edge.node.residual.residualSec,
              residualSecErr: edge.node.residual.residualSecErr,
              duration: edge.node.length,
              plotLink: run_result.plotLink,
              band: run_result.observation.band,
            });
          }
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
    id: row.id,
    utc: moment(mjdToUnixTimestamp(row.mjd)).valueOf(),
    day: row.dayOfYear,
    phase: row.binaryOrbitalPhase,
    value: row.residualSec * 1e6,
    error: row.residualSecErr * 1e9,
    size: row.duration,
    link: row.plotLink,
    band: row.band,
  }));

  return allData;
};
