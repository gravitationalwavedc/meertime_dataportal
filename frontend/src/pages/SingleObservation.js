import { QueryRenderer, graphql } from 'react-relay';

import React from 'react';
import SingleObservationTable from '../components/SingleObservationTable';
import environment from '../relayEnvironment';

const query = graphql`
  query SingleObservationQuery($jname: String!, $utc: String, $beam: Int) {
    foldObservationDetails(jname:$jname ,utc:$utc ,beam:$beam){
      edges {
        node {
          beam
          utc
          proposal
          frequency
          bw
          ra
          dec
          length
          nbin
          nchan
          tsubint
          nant
          profileHi
          phaseVsTimeHi
          phaseVsFrequencyHi
          bandpassHi
          snrVsTimeHi
          schedule
          phaseup
        }
      }
    }
  }`;

// Missing
// snrSpip

const SingleObservation = ({ match: { params: { jname, utc, beam } } }) => 
    <QueryRenderer
        environment={environment}
        query={query}
        variables={{
            jname: jname,
            utc: utc,
            beam: beam
        }}
        render = {({ props }) => props ? <SingleObservationTable data={props} jname={jname} /> : <h1>Loading...</h1>}
    />;

export default SingleObservation;
