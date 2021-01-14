import { QueryRenderer, graphql } from 'react-relay';

import FoldDetailTable from '../components/FoldDetailTable';
import MainLayout from '../components/MainLayout';
import React from 'react';
import environment from '../relayEnvironment';

const query = graphql`
  query FoldDetailQuery($jname: String!, $getProposalFilters: String) {
    relayObservationDetails(jname:$jname, getProposalFilters: $getProposalFilters) {
      jname
      totalObservations
      totalObservationHours
      totalProjects
      totalEstimatedDiskSpace
      totalTimespanDays
      ephemeris
      ephemerisUpdatedAt
      edges {
        node {
          id
          utc
          proposalShort
          length
          beam
          bw
          nchan
          band
          nbin
          nant
          nantEff
          dmFold
          dmPipe
          rmPipe
          snrPipe
          snrSpip
        }
      }
    }
  }`;

const FoldDetail = ({ match, relayEnvironment }) => {
    const { jname, project } = match.params;
    return (
        <MainLayout title={jname}>
            <QueryRenderer
                environment={relayEnvironment}
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
                        return <FoldDetailTable data={props} />;
                    }

                    return <h1>Loading...</h1>;
                }}
            />
        </MainLayout>
    );
};

FoldDetail.defaultProps = {
    relayEnvironment: environment
};

export default FoldDetail;
