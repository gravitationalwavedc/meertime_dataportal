import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SearchmodeDetailTable from "../components/SearchmodeDetailTable";

const query = graphql`
  query SearchmodeDetailQuery($jname: String!, $mainProject: String) {
    observationSummary(
      pulsar_Name: $jname
      obsType: "search"
      calibration_Id: "All"
      mainProject: $mainProject
      project_Short: "All"
      band: "All"
    ) {
      edges {
        node {
          observations
          projects
          observationHours
          timespanDays
        }
      }
    }
    observation(
      pulsar_Name: [$jname]
      mainProject: $mainProject
      obsType: "search"
    ) {
      edges {
        node {
          id
          utcStart
          project {
            short
          }
          raj
          decj
          beam
          duration
          frequency
          nantEff
          filterbankNbit
          filterbankNpol
          filterbankNchan
          filterbankTsamp
          filterbankDm
        }
      }
    }
  }
`;

const SearchmodeDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  const data = useLazyLoadQuery(query, {
    jname: jname,
    mainProject: mainProject,
  });

  return (
    <MainLayout title={jname}>
      <SearchmodeDetailTable
        data={data}
        jname={jname}
        mainProject={mainProject}
      />
    </MainLayout>
  );
};

export default SearchmodeDetail;
