import { QueryRenderer, graphql } from 'react-relay';

import React from 'react';
import SingleObservationTable from '../components/SingleObservationTable';
import environment from '../relayEnvironment';

const query = graphql`
  query SingleObservationQuery($jname: String!, $utc: String!, $beam: Int!) {
    relayObservationModel(jname:$jname ,utc:$utc ,beam:$beam){
      jname
      beam
      utc
      proposal
      frequency
      bw
      ra
      dec
      length
      snrSpip
      nbin
      nchan
      nsubint
      nant
      profile
      phaseVsTime
      phaseVsFrequency
      bandpass
      snrVsTime
      schedule
      phaseup
    }
  }`;

const SingleObservation = ({ match: { params: { jname, utc, beam } } }) => 
    <QueryRenderer
        environment={environment}
        query={query}
        variables={{
            jname: jname,
            utc: utc,
            beam: beam
        }}
        render = {({ props }) => props ? <SingleObservationTable data={props} /> : <h1>Loading...</h1>}
    />;

export default SingleObservation;
