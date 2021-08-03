import { Button, Card, Col, Row } from 'react-bootstrap';

import React from 'react';
import { kronosLink } from '../helpers';

const JobCard = ({ row }) => 
    <Card className="mb-3 shadow-md job-card" data-testid="job-card">
        <Card.Body>
            <Card.Title><span className="mr-3">{row.utc}</span> {row.proposalShort}</Card.Title>
            <Row>
                <Col>
                    <p className="overline mb-1">RA</p>
                    <p>{row.ra}</p>
                    <p className="overline mb-1">DEC</p>
                    <p>{row.dec}</p>
                </Col>
                <Col>
                    <p className="overline mb-1">Length</p>
                    <p>{row.length} minutes</p>
                    <p className="overline mb-1">Beam</p>
                    <p>{row.beam}</p>
                </Col>
                <Col>
                    <p className="overline mb-1">Frequency</p>
                    <p>{row.frequency} MHz</p>
                    <p className="overline mb-1">Nchan</p>
                    <p>{row.nchan}</p>
                </Col>
                <Col>
                    <p className="overline mb-1">Nbit</p>
                    <p>{row.nbit}</p>
                    <p className="overline mb-1">Nant Eff</p>
                    <p>{row.nantEff}</p>
                </Col>
                <Col>
                    <p className="overline mb-1">Npol</p>
                    <p>{row.npol}</p>
                    <p className="overline mb-1">DM</p>
                    <p>{row.dm}</p>
                    <p className="overline mb-1">tSamp</p>
                    <p>{row.tsamp}</p>
                </Col>
            </Row>
        </Card.Body>
        <Card.Footer>
            <Button 
                size="sm"
                as="a"
                href={kronosLink(row.beam, row.jname, row.utc)}
                variant="link"> 
                        View Kronos 
            </Button>
        </Card.Footer>
    </Card>;

export default JobCard;
