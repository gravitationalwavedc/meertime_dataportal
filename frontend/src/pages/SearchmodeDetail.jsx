import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SearchmodeDetailTable from "../components/SearchmodeDetailTable";

const query = graphql`
  query SearchmodeDetailQuery($jname: String!, $mainProject: String) {
    searchmodeObservationDetails(jname: $jname, mainProject: $mainProject) {
      totalObservations
      totalProjects
      totalTimespanDays
      edges {
        node {
          id
          utc
          project
          beam
          length
          tsamp
          frequency
          nchan
          nbit
          npol
          nantEff
          dm
          ra
          dec
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
      <SearchmodeDetailTable data={data} jname={jname} />
    </MainLayout>
  );
};

export default SearchmodeDetail;
