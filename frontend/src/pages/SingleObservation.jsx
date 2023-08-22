import { graphql, useLazyLoadQuery } from "react-relay";
import SingleObservationTable from "../components/SingleObservationTable";
import { performRefreshTokenMutation } from "./RefreshToken.jsx";

const query = graphql`
  query SingleObservationQuery($jname: String!, $utc: String, $beam: Int) {
    pulsarFoldResult(pulsar: $jname, utcStart: $utc, beam: $beam) {
      edges {
        node {
          observation{
            calibration {
              id
              idInt
            }
            beam
            utcStart
            obsType
            project {
              id
              short
              mainProject {
                name
              }
            }
            frequency
            bandwidth
            raj
            decj
            duration
            foldNbin
            foldNchan
            foldTsubint
            nant
          }
          images {
            edges {
              node {
                image
                cleaned
                imageType
                resolution
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
  router,
  match: {
    params: { jname, utc, beam },
  },
}) => {
  performRefreshTokenMutation(router);

  const data = useLazyLoadQuery(query, {
    jname: jname,
    utc: utc,
    beam: beam,
  });

  return <SingleObservationTable data={data} jname={jname} />;
};

export default SingleObservation;
