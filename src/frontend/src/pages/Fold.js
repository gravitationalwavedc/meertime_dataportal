import { QueryRenderer, graphql } from 'react-relay';

import FoldTable from '../components/FoldTable';
import MainLayout from '../components/MainLayout';
import React from 'react';
import environment from '../relayEnvironment';

const query = graphql`
  query FoldQuery {
    ...FoldTable_data
  }`;

const Fold = () =>
    <MainLayout title='Fold Observations'>
        <QueryRenderer
            environment={environment}
            query={query}
            fetchPolicy="store-and-network"
            render = {({ props }) => props ? <FoldTable data={props} /> : <h1>Loading...</h1>}
        />
    </MainLayout>;

export default Fold;
