import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SearchDetailTable from "../components/SearchDetailTable";
import { toApiFilter } from "../helpers";

const query = graphql`
  query SearchDetailQuery($jname: String!, $mainProject: String) {
    ...SearchDetailTableFragment
      @arguments(jname: $jname, mainProject: $mainProject)
  }
`;

const SearchDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  const data = useLazyLoadQuery(query, {
    jname: toApiFilter(jname),
    mainProject: toApiFilter(mainProject),
  });

  return (
    <MainLayout title={jname}>
      <SearchDetailTable data={data} jname={jname} mainProject={mainProject} />
    </MainLayout>
  );
};

export default SearchDetail;
