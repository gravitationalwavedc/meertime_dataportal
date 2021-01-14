import { QueryRenderer, graphql } from 'react-relay';

import React from 'react';
import SessionTable from '../components/SessionTable';
import environment from '../relayEnvironment';

const query = graphql`
  query SessionQuery {
    ...SessionTable_data
  }`;

const Session = () => (
    <QueryRenderer
        environment={environment}
        query={query}
        fetchPolicy="store-and-network"
        render = {({ props, error }) => {
            if (error) {
                return <React.Fragment>
                    <h1>404</h1> 
                    <h2>This Pulsar hasn&apos;t been discovered yet!</h2>
                    <h5 className="mt-3">Or maybe it just isn&apos;t in our database?</h5>
                </React.Fragment>;
            }

            if(props) {
                return <SessionTable data={props}/>;
            }

            return <h1>Loading...</h1>;
        }}
    />
);

export default Session;
