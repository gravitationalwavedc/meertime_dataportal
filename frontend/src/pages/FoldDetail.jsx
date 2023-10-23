import { graphql, useLazyLoadQuery } from "react-relay";
import FoldDetailTable from "../components/FoldDetailTable";
import MainLayout from "../components/MainLayout";

const query = graphql`
  query FoldDetailQuery {
  ...FoldDetailTable_data
}
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  console.log("jname:", jname);
  const data = useLazyLoadQuery(query, {});
  console.log("data:", data);

  return (
    <MainLayout title={jname}>
      <FoldDetailTable data={data} match={match} />
    </MainLayout>
  );
};

export default FoldDetail;
