import Plot from "react-plotly.js";
import { useRouter } from "found";
import {
  filterBandData,
  getActivePlotData,
  getPlotlyData,
  getXaxisFormatter,
  getYaxisLabel,
} from "./plotData";
import { graphql, useLazyLoadQuery } from "react-relay";

const plotQuery = graphql`
  query PlotlyPlotQuery(
    $pulsar: String!
    $mainProject: String
    $projectShort: String
    $excludeBadges: [String]
    $minimumSNR: Float
    $obsNchan: Int
  ) {
    pulsarFoldResult(
      pulsar: $pulsar
      mainProject: $mainProject
      minimumSNR: $minimumSNR
      excludeBadges: $excludeBadges
    ) {
      totalToa(
        pulsar: $pulsar
        mainProject: $mainProject
        projectShort: $projectShort
      )
      timingResidualPlotData(
        pulsar: $pulsar
        mainProject: $mainProject
        projectShort: $projectShort
        excludeBadges: $excludeBadges
        minimumSNR: $minimumSNR
        obsNchan: $obsNchan
      ) {
        utc
        band
        day
        size
        error
        snr
        value
        phase
        link
      }
      edges {
        node {
          observation {
            id
            utcStart
            dayOfYear
            binaryOrbitalPhase
            duration
            beam
            bandwidth
            nchan
            band
            foldNbin
            nant
            nantEff
            restricted
            embargoEndDate
            project {
              short
            }
            ephemeris {
              dm
            }
            calibration {
              idInt
            }
          }
          pipelineRun {
            dm
            dmErr
            rm
            rmErr
            sn
            flux
          }
        }
      }
    }
  }
`;
const PlotlyPlot = ({
  xAxis,
  activePlot,
  jname,
  mainProject,
  projectShort,
  excludeBadges,
  minimumSNR,
  nchan,
}) => {
  const queryData = useLazyLoadQuery(plotQuery, {
    pulsar: jname,
    mainProject: mainProject,
    projectShort: projectShort,
    excludeBadges: excludeBadges,
    minimumSNR: minimumSNR,
    obsNchan: nchan,
  });

  const data = getActivePlotData(queryData, activePlot, jname, mainProject);

  const { router } = useRouter();

  const handlePlotClick = (plotData) => {
    const link = plotData.points[0].customdata[1];
    if (link !== "" && link !== undefined) {
      router.push(link);
    }
  };

  const { plotData } = filterBandData(data);

  // Convert data into Plotly format based on x and y axis
  const plotlyData = getPlotlyData(plotData, xAxis, activePlot);

  const totalToaCount = queryData?.pulsarFoldResult?.totalToa;

  const calculatewRMS = (data) => {
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

  const wrmsValues = calculatewRMS(data);

  return (
    <>
      <p className="text-muted text-primary-600">
        {activePlot === "Timing Residuals"
          ? `Showing ${data.length} of ${totalToaCount} Time of Arrivals.`
          : null}
        {activePlot === "Timing Residuals" && (
          <ul>
            {Object.keys(wrmsValues).map((band) => (
              <li key={band}>
                {band} weighted RMS = {(wrmsValues[band] * 1e6).toFixed(1)} μs
              </li>
            ))}
          </ul>
        )}
      </p>
      <Plot
        data={plotlyData}
        layout={{
          title: activePlot,
          autosize: true,
          margin: {
            t: 40,
            r: 40,
            b: 60,
            l: 60,
          },
          paper_bgcolor: "rgba(1, 1, 1, 0)",
          plot_bgcolor: "rgba(1, 1, 1, 0)",
          xaxis: getXaxisFormatter(xAxis),
          yaxis: {
            title: {
              text: getYaxisLabel(activePlot),
            },
          },
          legend: { orientation: "h" },
        }}
        useResizeHandler={true}
        style={{ width: "100%", height: "100%" }}
        onClick={handlePlotClick}
        config={{
          displaylogo: false,
          displayModeBar: true,
          modeBarButtonsToRemove: ["resetScale2d"],
        }}
      />
    </>
  );
};

export default PlotlyPlot;
