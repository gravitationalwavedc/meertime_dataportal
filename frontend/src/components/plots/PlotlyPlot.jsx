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
    $excludeBadges: [String]
    $minimumSNR: Float
  ) {
    toa(
      pulsar: $pulsar
      mainProject: $mainProject
      excludeBadges: $excludeBadges
      minimumSNR: $minimumSNR
      nsubType: "1"
      obsNchan: 32
    ) {
      allNchans
      allProjects
      totalBadgeExcludedToas
      edges {
        node {
          observation {
            duration
            utcStart
            beam
            band
          }
          project {
            short
          }
          id
          obsNchan
          dmCorrected
          mjd
          snr
          dayOfYear
          binaryOrbitalPhase
          residualSec
          residualSecErr
          residualPhase
          residualPhaseErr
        }
      }
    }
    pulsarFoldResult(
      pulsar: $pulsar
      mainProject: $mainProject
      excludeBadges: $excludeBadges
      minimumSNR: $minimumSNR
    ) {
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
  excludeBadges,
  minimumSNR,
}) => {
  const queryData = useLazyLoadQuery(plotQuery, {
    pulsar: jname,
    mainProject: mainProject,
    excludeBadges: excludeBadges,
    minimumSNR: minimumSNR,
  });

  const data = getActivePlotData(queryData, activePlot, jname, mainProject);

  // const excludedToasCount = data?.toa?.totalBadgeExcludedToas;

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
  const excludedToasCount = queryData?.toa?.totalBadgeExcludedToas;
  return (
    <>
      <p className="text-muted text-primary-600">
        Filtered {excludedToasCount || 0} TOAs (Time of Arrivals) from the
        Observation Plot.
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
