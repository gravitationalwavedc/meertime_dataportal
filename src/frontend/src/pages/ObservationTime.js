import { QueryRenderer, graphql } from 'react-relay';

import ObservationTimeView from '../components/ObservationTimeView';
import React from 'react';
import environment from '../relayEnvironment';

const query = graphql`
  query ObservationTimeQuery {
    relayObservationModel(jname:"J1909-3744",utc:"2020-09-27-19:29:01",beam:4){
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

const Fold = () =>
    <QueryRenderer
        environment={environment}
        query={query}
        render = {({ props }) => props ? <ObservationTimeView data={props} /> : <h1>Loading...</h1>}
    />;

export default Fold;
