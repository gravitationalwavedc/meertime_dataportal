import { graphql, useLazyLoadQuery } from "react-relay";
import FoldDetailTable from "../components/FoldDetailTable";
import MainLayout from "../components/MainLayout";

const query = graphql`
  query FoldDetailQuery($jname: String!, $mainProject: String) {
    foldPulsar(jname: $jname, mainProject: $mainProject) {
      files {
        edges {
          node {
            project
            fileType
            size
            downloadLink
          }
        }
      }
    }
    foldObservationDetails(jname: $jname, mainProject: $mainProject) {
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
          id
          utc
          project
          ephemeris
          ephemerisIsUpdatedAt
          length
          beam
          bw
          nchan
          band
          nbin
          nant
          nantEff
          dmFold
          dmMeerpipe
          rmMeerpipe
          snBackend
          snMeerpipe
          flux
          restricted
          embargoEndDate
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
