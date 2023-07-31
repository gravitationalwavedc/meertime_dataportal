import { QueryRenderer, graphql } from "react-relay";

import FoldTable from "../components/FoldTable";
import MainLayout from "../components/MainLayout";
import environment from "../relayEnvironment";

const query = graphql`
  query FoldQuery {
    ...FoldTable_data
  }
`;

const Fold = ({ match }) => (
  <MainLayout title="Fold Observations">
    <QueryRenderer
      environment={environment}
      query={query}
      fetchPolicy="store-and-network"
      render={({ props }) => {
        return props ? (
          <FoldTable data={props} match={match} />
        ) : (
          <h1>Loading...</h1>
        );
      }}
    />
  </MainLayout>
);

export default Fold;