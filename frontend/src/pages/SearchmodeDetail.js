import { QueryRenderer, graphql } from 'react-relay';

import MainLayout from '../components/MainLayout';
import React from 'react';
import SearchmodeDetailTable from '../components/SearchmodeDetailTable';
import environment from '../relayEnvironment';

const query = graphql`
  query SearchmodeDetailQuery($jname: String!, $mainProject: String) {
    searchmodeObservationDetails(jname:$jname, mainProject: $mainProject) {
      totalObservations
      totalProjects
      totalTimespanDays
      edges {
        node {
          id
           utc
           project
           beam
           length
           tsamp
           frequency
           nchan
           nbit
           npol
           nantEff
           dm
           ra
           dec
        }
      }
    }
  }`;

const SearchmodeDetail = ({ match }) => {
    const { jname, mainProject } = match.params;
    return (<MainLayout title={jname}>
        <QueryRenderer
            environment={environment}
            query={query}
            variables={{
                jname: jname,
                mainProject: mainProject 
            }}
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
                    return <SearchmodeDetailTable data={props} jname={jname} />;
                }

                return <h1>Loading...</h1>;
            }}
        />
    </MainLayout>);
};

export default SearchmodeDetail;
