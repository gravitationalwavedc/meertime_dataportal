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
          project
          frequency
          bw
          ra
          dec
          length
          nbin
          nchan
          tsubint
          nant
          images {
            edges {
              node {
                plotType
                genericPlotType
                resolution
                process
                url
              }
            }
          }
        }
      }
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
        render={
            ({ error, props }) => {
                if (error) {
                    return <h5>{error.message}</h5>;
                } else if (props) {
                    return <SingleObservationTable data={props} jname={jname} />;
                }
                return <h1>Loading...</h1>;

            }
        }
    />;

export default SingleObservation;
