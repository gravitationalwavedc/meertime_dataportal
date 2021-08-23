import { Modal, Table } from 'react-bootstrap';

import React from 'react';
import { formatUTC } from '../helpers';

const Ephemeris = ({ ephemeris, updated, show, setShow }) => {
    const ephemerisJSON = JSON.parse(ephemeris);

    const EphemerisValue = ({ data }) => 
        <td className="ephemris-item">
            <span >{data['val']}</span>
            <span >{data['err']}</span>
        </td>;

    return (
        <Modal 
            className="ephemeris-table" 
            show={show} 
            onHide={() => setShow(false)} aria-labelledby="ephemeris-data">
            <Modal.Header style={{ borderBottom: 'none' }} closeButton>
                <Modal.Title className="text-primary">
                      Folding Ephemeris
                    <h6 className="text-muted">as of {formatUTC(updated)}</h6>
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table>
                    <tbody>
                        {Object.keys(ephemerisJSON).map((key) => 
                            <tr key={key}>
                                <th>{key}</th>
                                <EphemerisValue data={ephemerisJSON[key]}/>
                            </tr>)}
                    </tbody>
                </Table>
            </Modal.Body>
        </Modal>
    );
};

export default Ephemeris;
