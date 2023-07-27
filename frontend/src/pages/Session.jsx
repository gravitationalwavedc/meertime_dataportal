import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SessionTable from "../components/SessionTable";

const query = graphql`
  query SessionQuery($id: Int) {
    ...SessionTable_data @arguments(id: $id)
  }
`;

const getTitle = (id) => {
  if (id) return "Session";
  return "Last Session";
};

const Session = ({ match }) => {
  const { id } = match.params;

  return (
    <MainLayout title={getTitle(start, utc)}>
      <SessionTable data={data} utc={utc} />
    </MainLayout>
  );
};

export default Session;
