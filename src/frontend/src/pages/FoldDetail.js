import React from 'react';
import MainLayout from '../components/MainLayout';
import { graphql, QueryRenderer } from 'react-relay';
import environment from '../relayEnvironment';
import FoldDetailTable from '../components/FoldDetailTable';

const query = graphql`
  query FoldDetailQuery($jname: String!) {
    foldObservationDetails(jname:$jname) {
      jname
      totalObservations
      totalObservationHours
      totalProjects
      totalEstimatedDiskSpace
      totalTimespanDays
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

const FoldDetail = ({ match }) => {
    const jname = match.params.jname;
    return (<MainLayout title={jname}>
        <QueryRenderer
            environment={environment}
            query={query}
            variables={{
                jname: jname
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
    </MainLayout>);
};

export default FoldDetail;