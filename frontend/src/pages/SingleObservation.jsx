import { graphql, useLazyLoadQuery } from "react-relay";
import SingleObservationTable from "../components/SingleObservationTable";
import MainLayout from "../components/MainLayout";
import { Link } from "found";

const query = graphql`
  query SingleObservationQuery($pulsar: String!, $utc: String!, $beam: Int!) {
    ...SingleObservationTableFragment
      @arguments(pulsar: $pulsar, utc: $utc, beam: $beam)
    ...SingleObservationFileDownloadFragment
      @arguments(jname: $pulsar, utc: $utc, beam: $beam)
  }
`;

const SingleObservation = ({
  // router,
  match: {
    params: { jname, utc, beam },
  },
}) => {
  const data = useLazyLoadQuery(query, {
    pulsar: jname,
    utc: utc,
    beam: beam,
  });

  const title = (
    <Link size="sm" to={`/fold/meertime/${jname}/`}>
      {jname}
    </Link>
  );

  return (
    <MainLayout title={title}>
      <SingleObservationTable data={data} jname={jname} />
    </MainLayout>
  );
};

export default SingleObservation;
