import { graphql, useLazyLoadQuery } from "react-relay";
import SingleObservationTable from "../components/SingleObservationTable";
import environment from "../relayEnvironment";
// import { performRefreshTokenMutation } from "./RefreshToken.jsx";

const query = graphql`
  query SingleObservationQuery($jname: String!, $utc: String!, $beam: Int!) {
    foldObservationDetails(jname: $jname, utc: $utc, beam: $beam) {
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
    ...DownloadFluxcalButtons_data
      @arguments(jname: $jname, utc: $utc, beam: $beam)
  }
`;

const SingleObservation = ({
  // router,
  match: {
    params: { mainProject, jname, utc, beam },
  },
}) => {
  // performRefreshTokenMutation(router);

  const data = useLazyLoadQuery(query, {
    jname: jname,
    utc: utc,
    beam: beam,
  });

  return (
    <SingleObservationTable
      data={data}
      jname={jname}
      mainProject={mainProject}
    />
  );
};

export default SingleObservation;
