import { graphql, useLazyLoadQuery } from "react-relay";
import FoldDetailTable from "../components/FoldDetailTable";
import MainLayout from "../components/MainLayout";

const query = graphql`
  query FoldDetailQuery($jname: String!, $mainProject: String) {
    pulsarFoldResult(pulsar: $jname, mainProject: $mainProject) {
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
          }
        }
      }
    }
  }
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  const data = useLazyLoadQuery(query, {
    jname: jname,
    mainProject: mainProject,
  });

  return (
    <MainLayout title={jname}>
      <FoldDetailTable data={data} jname={jname} mainProject={mainProject} />
    </MainLayout>
  );
};

export default FoldDetail;
