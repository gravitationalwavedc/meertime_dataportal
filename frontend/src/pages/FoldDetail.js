import { QueryRenderer, graphql } from 'react-relay';

import FoldDetailTable from '../components/FoldDetailTable';
import MainLayout from '../components/MainLayout';
import React from 'react';
import environment from '../relayEnvironment';

const query = graphql`
  query FoldDetailQuery($jname: String!, $mainProject: String) {
    foldObservationDetails(jname:$jname, mainProject: $mainProject) {
      totalObservations
      totalObservationHours
      totalProjects
      totalEstimatedDiskSpace
      totalTimespanDays
      maxPlotLength
      minPlotLength
      description
      edges {
        node {
          id
          utc
          project
          ephemeris
          ephemerisIsUpdatedAt
          length
          beam
          bw
          nchan
          band
          nbin
          nant
          nantEff
          dmFold
          dmMeerpipe
          rmMeerpipe
          snBackend
          snMeerpipe
          flux
        }
      }
    }
  }`;

const FoldDetail = ({ match, relayEnvironment }) => {
    const { jname, mainProject } = match.params;
    return (
        <MainLayout title={jname}>
            <QueryRenderer
                environment={relayEnvironment}
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
                        </React.Fragment>;
                    }

                    if(props) {
                        return <FoldDetailTable data={props} jname={jname} />;
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
