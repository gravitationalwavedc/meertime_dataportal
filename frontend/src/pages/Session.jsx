import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SessionTable from "../components/session/SessionTable";

const sessionByIdQuery = graphql`
  query SessionQuery($id: Int) {
    ...SessionTable_data @arguments(id: $id)
  }
`;

const lastSessionQuery = graphql`
  query SessionLatestQuery {
    ...SessionTableLatest_data
  }
`;

const getTitle = (id) => {
  if (id) return "Session";
  return "Last Session";
};

const Session = ({ match }) => {
  const { id } = match.params;
  const isLatestSessionRoute = !id;
  const query = isLatestSessionRoute ? lastSessionQuery : sessionByIdQuery;
  const params = isLatestSessionRoute ? {} : { id: Number(id) };

  const data = useLazyLoadQuery(query, params);

  return (
    <MainLayout title={getTitle(id)}>
      <SessionTable data={data} isLatestSessionRoute={isLatestSessionRoute} />
    </MainLayout>
  );
};

export default Session;
