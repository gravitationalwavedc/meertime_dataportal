import { Modal, Table } from "react-bootstrap";
import { formatUTC } from "../helpers";
import { graphql, usePreloadedQuery } from "react-relay";
import { useEffect, useState } from "react";

export const ephemerisQuery = graphql`
  query EphemerisQuery($jname: String, $mainProject: String) {
    pulsarFoldResult(pulsar: $jname, mainProject: $mainProject) {
      residualEphemeris {
        id
        ephemerisData
        createdAt
      }
    }
  }
`;

const Ephemeris = ({ show, setShow, queryRef }) => {
  const data = usePreloadedQuery(ephemerisQuery, queryRef);
  const [updated, setUpdated] = useState("");
  const [ephemeris, setEphemeris] = useState({});

  useEffect(() => {
    const jsonData = data?.pulsarFoldResult?.residualEphemeris?.ephemerisData;
    if (jsonData !== undefined) {
      setEphemeris(
        JSON.parse(
          JSON.parse(data?.pulsarFoldResult?.residualEphemeris?.ephemerisData)
        )
      );
      setUpdated(
        formatUTC(data?.pulsarFoldResult?.residualEphemeris?.createdAt)
      );
    }
  }, [setUpdated, setEphemeris, data]);

  if (data.pulsarFoldResult.residualEphemeris === null) {
    return (
      <Modal
        className="ephemeris-table"
        show={show}
        onHide={() => setShow(false)}
        aria-labelledby="ephemeris-data"
      >
        <Modal.Header style={{ borderBottom: "none" }} closeButton>
          <Modal.Title className="text-primary">Folding Ephemeris</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <h5>No residual ephemeris data available.</h5>
        </Modal.Body>
      </Modal>
    );
  }

  return (
    <Modal
      className="ephemeris-table"
      show={show}
      onHide={() => setShow(false)}
      aria-labelledby="ephemeris-data"
    >
      <Modal.Header style={{ borderBottom: "none" }} closeButton>
        <Modal.Title className="text-primary">
          Folding Ephemeris
          <h6 className="text-muted">as of {updated}</h6>
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Table>
          <tbody>
            {Object.keys(ephemeris).map((key) =>
              key === "TIMEOFFSETS"
                ? ephemeris[key].map((item) => (
                    <tr key={item.id}>
                      <th>{key}</th>
                      <td className="ephemris-item">{item["type"]} </td>
                      <td className="ephemris-item">{item["mjd"]} </td>
                      <td className="ephemris-item">{item["display"]}</td>
                      <td className="ephemris-item">{item["offset"]} </td>
                      <td className="ephemris-item">{item["fit"]} </td>
                    </tr>
                  ))
                : !key.includes("_ERR") && (
                    <tr key={key}>
                      <th>{key}</th>
                      <td className="ephemris-item">{ephemeris[key]} </td>
                      <td className="ephemris-item">
                        {ephemeris[key + "_ERR"]}
                      </td>
                    </tr>
                  )
            )}
          </tbody>
        </Table>
      </Modal.Body>
    </Modal>
  );
};

export default Ephemeris;
