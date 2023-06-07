import { QueryRenderer, graphql } from "react-relay";

import MainLayout from "../components/MainLayout";
import React from "react";
import SessionTable from "../components/SessionTable";
import environment from "../relayEnvironment";

const query = graphql`
  query SessionQuery($start: String, $end: String, $utc: String) {
    ...SessionTable_data @arguments(start: $start, end: $end, utc: $utc)
  }
`;

const getTitle = (start, utc) => {
  if (start || utc) return "Session";
  return "Last Session";
};

const Session = ({ match }) => {
  const { start, end, utc } = match.params;
  return (
    <MainLayout title={getTitle(start, utc)}>
      <QueryRenderer
        environment={environment}
        query={query}
        variables={{
          start: start ? start : null,
          end: end ? end : null,
          utc: utc ? utc : null,
        }}
        fetchPolicy="store-and-network"
        render={({ props, error }) => {
          if (error) {
            return (
              <React.Fragment>
                <h1>404</h1>
              </React.Fragment>
            );
          }

          if (props) {
            return <SessionTable data={props} utc={utc} />;
          }

          return <h1>Loading...</h1>;
        }}
      />
    </MainLayout>
  );
};

export default Session;
