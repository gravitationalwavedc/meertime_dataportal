import { QueryRenderer, graphql } from "react-relay";
import MainLayout from "../components/MainLayout";
import React from "react";
import SessionListTable from "../components/SessionListTable";
import environment from "../relayEnvironment";

const query = graphql`
  query SessionListTableQuery {
    ...SessionListTable_data
  }
`;

const SessionList = () => (
  <MainLayout title="Sessions">
    <QueryRenderer
      environment={environment}
      query={query}
      render={({ props, error }) => {
        if (error) {
          return <h1>404</h1>;
        }

        if (props) {
          return <SessionListTable data={props} />;
        }

        return <h1>Loading...</h1>;
      }}
    />
  </MainLayout>
);

export default SessionList;
