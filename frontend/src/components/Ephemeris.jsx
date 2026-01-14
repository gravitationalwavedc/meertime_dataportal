import { graphql, usePreloadedQuery } from "react-relay";
import EphemerisModal from "./EphemerisModal";

export const ephemerisQuery = graphql`
  query EphemerisQuery($jname: String, $mainProject: String) {
    pulsarFoldResult(pulsar: $jname, mainProject: $mainProject) {
      foldingEphemeris {
        id
        ephemerisData
        createdAt
        project {
          short
        }
      }
      foldingEphemerisIsEmbargoed
      foldingEphemerisExistsButInaccessible
    }
  }
`;

const Ephemeris = ({ show, setShow, queryRef }) => {
  const data = usePreloadedQuery(ephemerisQuery, queryRef);

  return <EphemerisModal show={show} setShow={setShow} data={data} />;
};

export default Ephemeris;
