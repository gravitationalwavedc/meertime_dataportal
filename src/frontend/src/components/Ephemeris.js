import { Modal, Table } from 'react-bootstrap';

import React from 'react';
import moment from 'moment';

const Ephemeris = ({ ephemeris, updated, show, setShow }) => {
    const ephemerisJSON = JSON.parse(ephemeris);
    const EphemerisValue = ({ data }) => 
        <td className="ephemris-item">
            {data.map((value) => <span key={value}>{value}</span>)}
        </td>;

    const updatedFormated = moment.parseZone(updated, moment.ISO_8601).format('YYYY-MM-DD-HH:mm:ss');

    return (
        <Modal size="xl" show={show} onHide={() => setShow(false)} aria-labelledby="ephemeris-data">
            <Modal.Header style={{ borderBottom: 'none' }} closeButton>
                <Modal.Title className="text-primary">
                  Folding Ephemeris
                    <h6 className="text-muted">as of {updatedFormated}</h6>
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table striped className="ephemeris-table">
                    <tbody>
                        {Object.keys(ephemerisJSON).map((key) => 
                            <tr key={key}><th>{key}</th><EphemerisValue data={ephemerisJSON[key]}/></tr>)}
                    </tbody>
                </Table>
            </Modal.Body>
        </Modal>
    );
};

export default Ephemeris;
