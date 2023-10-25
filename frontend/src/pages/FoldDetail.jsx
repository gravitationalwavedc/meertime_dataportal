import { graphql, useLazyLoadQuery } from "react-relay";
import FoldDetailTable from "../components/FoldDetailTable";
import MainLayout from "../components/MainLayout";

const tableQuery = graphql`
query FoldDetailQuery(
  $jname: String!,
  $mainProject: String
  $dmCorrected: Boolean,
  $minimumNsubs: Boolean,
  $obsNchan: Int,
) {
  observationSummary (
    pulsar_Name: $jname,
    obsType: "fold",
    calibration_Id: "All",
    mainProject: $mainProject,
    project_Short: "All",
    band: "All",
  ) {
    edges {
      node {
        observations
        observationHours
        projects
        pulsars
        estimatedDiskSpaceGb
        timespanDays
        maxDuration
        minDuration
      }
    }
  }
  pulsarFoldResult(
      pulsar: $jname,
      mainProject: $mainProject
    ) {
    residualEphemeris {
      ephemerisData
      createdAt
    }
    description
    toasLink
    edges {
      node {
        observation{
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
          toas (
            dmCorrected: $dmCorrected,
            minimumNsubs: $minimumNsubs,
            obsNchan: $obsNchan,
          ){
            edges {
              node {
                freqMhz
                length
                residual {
                  mjd
                  dayOfYear
                  binaryOrbitalPhase
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
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  console.log("jname:", jname);
  console.log("mainProject:", mainProject);
  const tableData   = useLazyLoadQuery(tableQuery, {
    jname: jname,
    mainProject: mainProject,
  });

  return (
    <MainLayout title={jname}>
      <FoldDetailTable tableData={tableData} jname={jname} mainProject={mainProject} />
    </MainLayout>
  );
};

export default FoldDetail;
