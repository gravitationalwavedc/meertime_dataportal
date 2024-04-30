import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SessionTable from "../components/session/SessionTable";

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

  let params;
  if (id) {
    params = { id: id };
  } else {
    params = { id: -1 };
  }

  const data = useLazyLoadQuery(query, params);

  return (
    <MainLayout title={getTitle(id)}>
      <SessionTable data={data} id={id} />
    </MainLayout>
  );
};

export default Session;
