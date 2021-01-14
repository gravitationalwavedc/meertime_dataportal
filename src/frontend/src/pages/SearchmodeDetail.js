import { QueryRenderer, graphql } from 'react-relay';

import MainLayout from '../components/MainLayout';
import React from 'react';
import SearchmodeDetailTable from '../components/SearchmodeDetailTable';
import environment from '../relayEnvironment';

const query = graphql`
  query SearchmodeDetailQuery($jname: String!, $getProposalFilters: String) {
    relaySearchmodeDetails(jname:$jname, getProposalFilters: $getProposalFilters) {
      jname
      totalObservations
      totalObservationHours
      totalProjects
      totalTimespanDays
      ephemeris
      ephemerisUpdatedAt
      edges {
        node {
          id
           utc
           proposalShort
           beam
           comment
           length
           tsamp
           bw
           frequency
           nchan
           nbit
           npol
           nant
           nantEff
           dm
           ra
           dec
        }
      }
    }
  }`;

const SearchmodeDetail = ({ match }) => {
    const { jname, project } = match.params;
    return (<MainLayout title={jname}>
        <QueryRenderer
            environment={environment}
            query={query}
            variables={{
                jname: jname,
                getProposalFilters: project
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
                    return <SearchmodeDetailTable data={props} />;
                }

                return <h1>Loading...</h1>;
            }}
        />
    </MainLayout>);
};

export default SearchmodeDetail;
