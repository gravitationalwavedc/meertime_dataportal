import { Modal, Table } from "react-bootstrap";
import { formatUTC } from "../helpers";

const Ephemeris = ({ ephemeris, updated, show, setShow }) => {
  const ephemerisJSON = JSON.parse(JSON.parse(ephemeris));

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
          <h6 className="text-muted">as of {formatUTC(updated)}</h6>
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Table>
          <tbody>
            {Object.keys(ephemerisJSON).map((key, index) => (
              key === "TIMEOFFSETS" ? (
                ephemerisJSON[key].map((item, index) => (
                  <tr key={index}>
                    <th>{key}</th>
                    <td className="ephemris-item">{item["type"]}   </td>
                    <td className="ephemris-item">{item["mjd"]}    </td>
                    <td className="ephemris-item">{item["display"]}</td>
                    <td className="ephemris-item">{item["offset"]} </td>
                    <td className="ephemris-item">{item["fit"]}    </td>
                  </tr>
                ))
              ) : (!key.includes("_ERR") && (
                <tr key={key}>
                  <th>{key}</th>
                  <td className="ephemris-item">{ephemerisJSON[key]}        </td>
                  <td className="ephemris-item">{ephemerisJSON[key + "_ERR"]}</td>
                </tr>
              ))
            ))}
          </tbody>
        </Table>
      </Modal.Body>
    </Modal>
  );
};

export default Ephemeris;
