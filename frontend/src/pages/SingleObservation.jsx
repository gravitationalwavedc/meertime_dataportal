import { graphql, useLazyLoadQuery } from "react-relay";
import SingleObservationTable from "../components/SingleObservationTable";
import environment from "../relayEnvironment";
// import { performRefreshTokenMutation } from "./RefreshToken.jsx";

const query = graphql`
  query SingleObservationQuery($pulsar: String!, $utc: String!, $beam: Int!) {
    ...SingleObservationTableFragment
      @arguments(pulsar: $pulsar, utc: $utc, beam: $beam)
    ...DownloadFluxcalButtons_data
      @arguments(jname: $pulsar, utc: $utc, beam: $beam)
  }
`;

const SingleObservation = ({
  // router,
  match: {
    params: { jname, utc, beam },
  },
}) => {
  // performRefreshTokenMutation(router);

  const data = useLazyLoadQuery(query, {
    pulsar: jname,
    utc: utc,
    beam: beam,
  });

  return <SingleObservationTable data={data} jname={jname} />;
};

export default SingleObservation;
