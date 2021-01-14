import { Modal, Table } from 'react-bootstrap';

import React from 'react';
import { formatUTC } from '../helpers';

const Ephemeris = ({ ephemeris, updated, show, setShow }) => {
    const ephemerisJSON = JSON.parse(ephemeris);
    const EphemerisValue = ({ data }) => 
        <td className="ephemris-item">
            {data.map((value) => <span key={value}>{value}</span>)}
        </td>;

    return (
        <Modal size="xl" show={show} onHide={() => setShow(false)} aria-labelledby="ephemeris-data">
            <Modal.Header style={{ borderBottom: 'none' }} closeButton>
                <Modal.Title className="text-primary">
                  Folding Ephemeris
                    <h6 className="text-muted">as of {formatUTC(updated)}</h6>
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table className="ephemeris-table">
                    <tbody>
                        {Object.keys(ephemerisJSON).map((key) => 
                            <tr key={key}>
                                <th style={{ textAlign: 'right' }}>{key}</th>
                                <EphemerisValue data={ephemerisJSON[key]}/>
                            </tr>)}
                    </tbody>
                </Table>
            </Modal.Body>
        </Modal>
    );
};

export default Ephemeris;
