import { QueryRenderer, graphql } from 'react-relay';

import MainLayout from '../components/MainLayout';
import React from 'react';
import SearchTable from '../components/SearchTable';
import environment from '../relayEnvironment';

const query = graphql`
  query SearchQuery {
    ...SearchTable_data
  }`;

const Search = () =>
    <MainLayout title='Searchmode Observations'>
        <QueryRenderer
            environment={environment}
            query={query}
            render = {({ props }) => props ? <SearchTable data={props} /> : <h1>Loading...</h1>}
        />
    </MainLayout>;

export default Search;
