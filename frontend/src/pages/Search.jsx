import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SearchTable from "../components/SearchTable";

const query = graphql`
  query SearchQuery {
    ...SearchTable_data
  }
`;

const Search = () => {
  const data = useLazyLoadQuery(query, {});
  return (
    <MainLayout title="Search Mode Observations">
      <SearchTable data={data} />
    </MainLayout>
  );
};

export default Search;
