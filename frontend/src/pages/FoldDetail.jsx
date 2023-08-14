import { graphql, useLazyLoadQuery } from "react-relay";
import FoldDetailTable from "../components/FoldDetailTable";
import MainLayout from "../components/MainLayout";

const query = graphql`
  query FoldDetailQuery(
      $jname: String!,
      $mainProject: String
      $dmCorrected: Boolean,
      $minimumNsubs: Boolean,
      $obsNchan: Int,
    ) {
    pulsarFoldResult(
        pulsar: $jname,
        mainProject: $mainProject
      ) {
      totalObservations
      totalObservationHours
      totalProjects
      totalEstimatedDiskSpace
      totalTimespanDays
      maxPlotLength
      minPlotLength
      description
      ephemerisLink
      toasLink
      edges {
        node {
          observation{
            utcStart
            duration
            beam
            bandwidth
            nchan
            band
            foldNbin
            nant
            nantEff
            project{
              short
            }
            ephemeris {
              dm
            }
          }
          pipelineRun{
            dm
            dmErr
            rm
            rmErr
            sn
            flux
            ephemeris {
              ephemerisData
            }
            toas (
              dmCorrected: $dmCorrected,
              minimumNsubs: $minimumNsubs,
              obsNchan: $obsNchan,
            ){
              edges {
                node {
                  freqMhz
                  mjd
                  mjdErr
                  length
                  residuals {
                    edges {
                      node {
                        mjd
                        residualSec
                        residualSecErr
                        residualPhase
                        residualPhaseErr
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  const dmCorrected = false;
  const minimumNsubs = true;
  const obsNchan = 4;
  const data = useLazyLoadQuery(query, {
    jname: jname,
    mainProject: mainProject,
    dmCorrected: dmCorrected,
    minimumNsubs: minimumNsubs,
    obsNchan: obsNchan,
  });

  return (
    <MainLayout title={jname}>
      <FoldDetailTable data={data} jname={jname} mainProject={mainProject} />
    </MainLayout>
  );
};

export default FoldDetail;
