import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";

import FoldTable from "../components/FoldTable";
import MainLayout from "../components/MainLayout";

const query = graphql`
  query FoldQuery {
    ...FoldTable_data
  }
`;

const Fold = ({ match }) => {
  const data = useLazyLoadQuery(query, {});

  return (
    <MainLayout title="Fold Observations">
      <Suspense
        fallback={
          <div>
            <h3>Loading..</h3>
          </div>
        }
      >
        <FoldTable data={data} match={match} />
      </Suspense>
    </MainLayout>
  );
};

export default Fold;
