import { calculateMedian, mjdToUnixTimestamp, formatUTC } from "../../helpers";
import moment from "moment";

export const getXaxisFormatter = (xAxis) => {
  if (xAxis === "utc") {
    return {
      title: {
        text: getXaxisLabel(xAxis),
      },
      type: "date",
      tickformat: "%Y",
      dtick: "M12",
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
      type: "date",
      tickformat: "%Y",
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
  } else if (yAxis === "Timing Residuals") {
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
  } else if (yAxis === "Timing Residuals") {
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
  } else if (yAxis === "Timing Residuals") {
    const absMax = Math.max(Math.abs(minValue), Math.abs(maxValue));
    return [-absMax, -absMax * 0.5, 0, absMax * 0.5, absMax];
  }
};

export const getActivePlotData = (
  tableData,
  toaDataResult,
  activePlot,
  timingProject,
  jname,
  mainProject
) => {
  if (activePlot == "Timing Residuals") {
    return residualPlotData(toaDataResult, timingProject, jname, mainProject);
  } else if (activePlot == "S/N") {
    return snrPlotData(tableData);
  } else if (activePlot == "Flux Density") {
    return fluxPlotData(tableData);
  } else if (activePlot == "DM") {
    return dmPlotData(tableData);
  } else if (activePlot == "RM") {
    return rmPlotData(tableData);
  } else {
    console.error(`Unknown activePlot: ${activePlot}`);
    return [];
  }
};

export const filterBandData = (data) => {
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

  const otherData = data.filter((row) => row.band === "OTHER");
  console.log("otherData", otherData);
  const other = {
    data: otherData,
    name: "OTHER",
    colour: "#808080",
    shape: "circle",
  };

  const UHFNSData = data.filter((row) => row.band === "UHF_NS");
  const UHFNS = {
    data: UHFNSData,
    name: "UHF_NS",
    colour: "#0d0887",
    shape: "square",
  };

  const minValue = Math.min(...data.map((row) => row.value - (row.error || 0)));

  const maxValue = Math.max(...data.map((row) => row.value + (row.error || 0)));

  const medianValue = calculateMedian(data);

  const unsortedTicks = Array.from(
    new Set(data.map((row) => moment(moment(row.utc).format("YYYY")).valueOf()))
  );
  const ticks = unsortedTicks.sort((a, b) => a - b);

  const plotData = [
    lBand,
    UHF,
    sband0,
    sband1,
    sband2,
    sband3,
    sband4,
    other,
    UHFNS,
  ];

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

export const residualPlotData = (data, timingProject, jname, mainProject) => {
  const allData = data.toa.edges
    .filter((edge) => edge.node.residualSec !== null)
    .filter((edge) => edge.node.project.short === timingProject)
    .map((edge) => ({
      id: edge.node.id,
      utc: moment(mjdToUnixTimestamp(edge.node.mjd)).valueOf(),
      day: edge.node.dayOfYear,
      phase: edge.node.binaryOrbitalPhase,
      value: edge.node.residualSec,
      error: edge.node.residualSecErr,
      size: edge.node.observation.duration,
      link: `/${mainProject}/${jname}/${formatUTC(
        edge.node.observation.utcStart
      )}/${edge.node.observation.beam}/`,
      band: edge.node.observation.band,
    }));

  return allData;
};
