import { QueryRenderer, graphql } from 'react-relay';

import MainLayout from '../components/MainLayout';
import React from 'react';
import SessionTable from '../components/SessionTable';
import environment from '../relayEnvironment';

const query = graphql`
  query SessionQuery {
    ...SessionTable_data
  }`;

const Session = () => (
    <MainLayout title='Last Session' >
        <QueryRenderer
            environment={environment}
            query={query}
            fetchPolicy="store-and-network"
            render = {({ props, error }) => {
                if (error) {
                    return <React.Fragment>
                        <h1>404</h1> 
                    </React.Fragment>;
                }

                if(props) {
                    return <SessionTable data={props}/>;
                }

                return <h1>Loading...</h1>;
            }}
        />
    </MainLayout>
);

export default Session;
