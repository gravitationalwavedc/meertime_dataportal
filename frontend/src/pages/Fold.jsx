import { graphql, useLazyLoadQuery } from "react-relay";

import FoldTable from "../components/FoldTable";
import MainLayout from "../components/MainLayout";

const query = graphql`
  query FoldQuery {
    ...FoldTableFragment
  }
`;

const Fold = ({ match }) => {
  const data = useLazyLoadQuery(query, {});

  return (
    <MainLayout title="Fold Observations">
      <FoldTable data={data} match={match} />
    </MainLayout>
  );
};

export default Fold;
