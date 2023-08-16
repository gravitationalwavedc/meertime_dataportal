import { graphql, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import SessionTable from "../components/SessionTable";

const query = graphql`
  query SessionQuery($start: String, $end: String, $utc: String) {
    ...SessionTable_data @arguments(start: $start, end: $end, utc: $utc)
  }
`;

const getTitle = (start, utc) => (start || utc ? "Session" : "Last Session");

const Session = ({ match }) => {
  const data = useLazyLoadQuery(query, {
    start: start || null,
    end: end || null,
    utc: utc || null,
  });
  const { start, end, utc } = match.params;

  return (
    <MainLayout title={getTitle(start, utc)}>
      <SessionTable data={data} utc={utc} />
    </MainLayout>
  );
};

export default Session;
