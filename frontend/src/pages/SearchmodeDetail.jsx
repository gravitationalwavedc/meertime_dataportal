import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SearchmodeDetailTable from "../components/SearchmodeDetailTable";

const query = graphql`
  query SearchmodeDetailQuery(
    $jname: String!,
    $mainProject: String
  ) {
    ...SearchmodeDetailTableFragment
      @arguments(
        jname: $jname
        mainProject: $mainProject
      )
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
