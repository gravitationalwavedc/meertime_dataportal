import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SessionListTable from "../components/SessionListTable";

const query = graphql`
  query SessionListTableQuery {
    ...SessionListTable_data
  }
`;

const SessionList = () => {
  const data = useLazyLoadQuery(query, {});

  return (
    <MainLayout title="Sessions">
      <SessionListTable data={data} />
    </MainLayout>
  );
};

export default SessionList;
