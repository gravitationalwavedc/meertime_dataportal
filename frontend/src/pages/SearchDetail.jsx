import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SearchDetailTable from "../components/SearchDetailTable";

const query = graphql`
  query SearchDetailQuery($jname: String!, $mainProject: String) {
    ...SearchDetailTableFragment
      @arguments(jname: $jname, mainProject: $mainProject)
  }
`;

const SearchDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  const data = useLazyLoadQuery(query, {
    jname: jname,
    mainProject: mainProject,
  });

  return (
    <MainLayout title={jname}>
      <SearchDetailTable data={data} jname={jname} mainProject={mainProject} />
    </MainLayout>
  );
};

export default SearchDetail;
