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
    return "Residual (s)";
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
  toaDataResult,
  activePlot,
  jname,
  mainProject
) => {
  if (activePlot == "Timing Residuals") {
    // Convert to milliseconds here because python struggles with large ints
    return toaDataResult?.pulsarFoldResult?.timingResidualPlotData?.map(
      (toa) => ({
        ...toa,
        utc: toa.utc * 1000,
      })
    );
  } else if (activePlot == "S/N") {
    return snrPlotData(toaDataResult, jname, mainProject);
  } else if (activePlot == "Flux Density") {
    return fluxPlotData(toaDataResult, jname, mainProject);
  } else if (activePlot == "DM") {
    return dmPlotData(toaDataResult, jname, mainProject);
  } else if (activePlot == "RM") {
    return rmPlotData(toaDataResult, jname, mainProject);
  } else {
    return [];
  }
};

export const filterBandData = (originalData) => {
  const data = originalData.filter((row) => row.value !== null);

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
    name: "LBAND",
    data: lBandData,
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

export const snrPlotData = (data, jname, mainProject) => {
  return data.pulsarFoldResult.edges.map(({ node }) => ({
    id: node.observation.id,
    utc: moment(node.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: node.observation.dayOfYear,
    phase: node.observation.binaryOrbitalPhase,
    value: node.pipelineRun.sn,
    size: node.observation.duration,
    link: `/${mainProject}/${jname}/${formatUTC(node.observation.utcStart)}/${
      node.observation.beam
    }/`,
    band: node.observation.band,
  }));
};

export const fluxPlotData = (data, jname, mainProject) => {
  return data.pulsarFoldResult.edges.map(({ node }) => ({
    id: node.observation.id,
    utc: moment(node.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: node.observation.dayOfYear,
    phase: node.observation.binaryOrbitalPhase,
    value: node.pipelineRun.flux,
    size: node.observation.duration,
    link: `/${mainProject}/${jname}/${formatUTC(node.observation.utcStart)}/${
      node.observation.beam
    }/`,
    band: node.observation.band,
  }));
};

export const dmPlotData = (data, jname, mainProject) => {
  return data.pulsarFoldResult.edges.map(({ node }) => ({
    id: node.observation.id,
    utc: moment(node.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: node.observation.dayOfYear,
    phase: node.observation.binaryOrbitalPhase,
    value: node.pipelineRun.dm,
    error: node.pipelineRun.dmErr,
    size: node.observation.duration,
    link: `/${mainProject}/${jname}/${formatUTC(node.observation.utcStart)}/${
      node.observation.beam
    }/`,
    band: node.observation.band,
  }));
};

export const rmPlotData = (data, jname, mainProject) => {
  return data.pulsarFoldResult.edges.map(({ node }) => ({
    id: node.observation.id,
    utc: moment(node.observation.utcStart, "YYYY-MM-DD-HH:mm:ss").valueOf(),
    day: node.observation.dayOfYear,
    phase: node.observation.binaryOrbitalPhase,
    value: node.pipelineRun.rm,
    error: node.pipelineRun.rmErr,
    size: node.observation.duration,
    link: `/${mainProject}/${jname}/${formatUTC(node.observation.utcStart)}/${
      node.observation.beam
    }/`,
    band: node.observation.band,
  }));
};

export const residualPlotData = (data, jname, mainProject) => {
  return data.toa.edges
    .filter(({ node }) => node.residualSec !== null)
    .map(({ node }) => ({
      id: node.id,
      utc: moment(mjdToUnixTimestamp(node.mjd)).valueOf(),
      day: node.dayOfYear,
      phase: node.binaryOrbitalPhase,
      value: node.residualSec,
      error: node.residualSecErr,
      size: node.observation.duration,
      link: `/${mainProject}/${jname}/${formatUTC(node.observation.utcStart)}/${
        node.observation.beam
      }/`,
      snr: node.snr,
      band: node.observation.band,
    }));
};

export const getPlotlyData = (plotData, xAxis, activePlot) =>
  plotData.reduce((data, dataBand) => {
    const sizes = dataBand.data.map((point) => point.size);

    // Set size scale from max size
    let sizeScale;
    if (sizes.length > 0) {
      const max = Math.max(...sizes);
      sizeScale = max / 30;
    } else {
      sizeScale = 1;
    }
    // Set x data
    let xData;

    if (xAxis === "utc") {
      xData = dataBand.data.map((point) => point.utc);
    } else if (xAxis === "day") {
      xData = dataBand.data.map((point) => point.day);
    } else if (xAxis === "phase") {
      xData = dataBand.data.map((point) => point.phase);
    } else {
      xData = dataBand.data.utc;
    }

    // Hover Template Vars
    const xAxisTemplateData = xAxis === "utc" ? "|%Y-%m-%d %H:%M:%S.%f" : "";
    const yAxixTemplateData =
      activePlot === "Timing Residuals"
        ? "<br>ToA S/N: %{customdata[2]:.4f}"
        : "";

    const row = {
      id: dataBand.data.map((point) => point.id),
      x: xData,
      error_y: {
        array: dataBand.data.map((point) => point.error),
        width: 6,
      },
      y: (xData = dataBand.data.map((point) => point.value)),
      customdata: dataBand.data.map((point) => [
        point.size,
        point.link,
        point.snr,
      ]),
      type: "scatter",
      mode: "markers",
      name: dataBand.name,
      hovertemplate: `${getXaxisLabel(
        xAxis
      )}: %{x${xAxisTemplateData}}<br>${getYaxisLabel(
        activePlot
      )}: %{y:.4f}${yAxixTemplateData}<br>Integration Time (s): %{customdata[0]:.4f}<br>S/N: %{customdata[2]}<extra></extra>`,
      marker: {
        color: dataBand.colour,
        symbol: dataBand.shape,
        size: dataBand.data.map((point) => point.size),
        sizeref: sizeScale,
        sizemin: 3,
      },
    };
    return [...data, { ...row }];
  }, []);

export const calculatewRMS = (data) => {
  const bandData = {};

  // Step 1: Calculate weighted mean for each band
  data.forEach((item) => {
    const { band, value, error } = item;
    if (!bandData[band]) {
      bandData[band] = { sum: 0, weightSum: 0, values: [] };
    }
    const weight = 1 / error ** 2;
    bandData[band].sum += value * weight;
    bandData[band].weightSum += weight;
    bandData[band].values.push({ value, weight });
  });

  const bandwRMS = {};

  Object.keys(bandData).forEach((band) => {
    const weightedMean = bandData[band].sum / bandData[band].weightSum;

    // Step 2: Calculate weighted RMS with the weighted mean subtracted
    let sum = 0;
    let weightSum = 0;
    bandData[band].values.forEach(({ value, weight }) => {
      sum += weight * (value - weightedMean) ** 2;
      weightSum += weight;
    });

    bandwRMS[band] = Math.sqrt(sum / weightSum);
  });

  return bandwRMS;
};
