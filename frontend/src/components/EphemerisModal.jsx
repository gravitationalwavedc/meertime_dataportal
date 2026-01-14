import { Modal, Table } from "react-bootstrap";
import { formatUTC } from "../helpers";
import { useEffect, useState } from "react";

const EphemerisModal = ({ show, setShow, data }) => {
  const [updated, setUpdated] = useState("");
  const [ephemeris, setEphemeris] = useState({});
  const projectShort = data?.pulsarFoldResult?.foldingEphemeris?.project.short;
  const isFromEmbargoedObservation =
    data?.pulsarFoldResult?.foldingEphemerisIsEmbargoed;
  const existsButInaccessible =
    data?.pulsarFoldResult?.foldingEphemerisExistsButInaccessible;

  useEffect(() => {
    const jsonData = data?.pulsarFoldResult?.foldingEphemeris?.ephemerisData;
    if (jsonData !== undefined) {
      setEphemeris(
        JSON.parse(
          JSON.parse(data?.pulsarFoldResult?.foldingEphemeris?.ephemerisData)
        )
      );
      setUpdated(
        formatUTC(data?.pulsarFoldResult?.foldingEphemeris?.createdAt)
      );
    }
  }, [setUpdated, setEphemeris, data]);

  // Determine the access message based on embargo status
  const getAccessMessage = () => {
    if (isFromEmbargoedObservation === true) {
      return "You have access to this embargoed ephemeris as a project member. It is the ephemeris used by MeerPipe's latest run.";
    }
    return "This is the latest publicly available ephemeris used by MeerPipe.";
  };

  if (data.pulsarFoldResult.foldingEphemeris === null) {
    return (
      <Modal
        className="ephemeris-table"
        show={show}
        onHide={() => setShow(false)}
        aria-labelledby="ephemeris-data"
      >
        <Modal.Header style={{ borderBottom: "none" }} closeButton>
          <Modal.Title className="text-primary">
            MeerPipe Folding Ephemeris
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {existsButInaccessible ? (
            <>
              <h5>
                No non-embargoed MeerPipe folding ephemeris data available to
                you.
              </h5>
              <p>
                Please request to join the relevant project for access at{" "}
                <a
                  href="https://pulsars.org.au/projects/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  https://pulsars.org.au/projects/
                </a>
                .
              </p>
            </>
          ) : (
            <h5>No MeerPipe folding ephemeris data available.</h5>
          )}
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
          MeerPipe Folding Ephemeris
          <h6 className="text-muted">
            Created at {updated} from project {projectShort}.
          </h6>
          <h6 className="text-muted">{getAccessMessage()}</h6>
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

export default EphemerisModal;
