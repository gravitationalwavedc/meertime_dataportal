import React from 'react';
import { Button, Card, Row, Col } from 'react-bootstrap';

const JobCard = ({ row }) => 
    <Card className="mb-3 shadow-md">
        <Card.Body>
            <Card.Title>{row.jname} {row.proposalShort}</Card.Title>
            <Row>
                <Col>
                    <p>Last Observation</p>
                    <p>{row.last}</p>
                </Col>
                <Col>
                    <Card.Text>Last S/N raw {row.latestSnr}</Card.Text>
                </Col>
                <Col>
                    <Card.Text>Total Observations {row.nobs}</Card.Text>
                </Col>
                <Col>
                    <Card.Text>Timespan {row.timespan}</Card.Text>
                </Col>
            </Row>
        </Card.Body>
        <Card.Footer>
            <Row className="justify-content-end">
                <Col md={4}>
                    <Button variant="secondary">Download CSV</Button>
                    <Button>View Meerwatch</Button>
                    <Button>View Observations</Button>
                </Col>
            </Row>
        </Card.Footer>
    </Card>;

export default JobCard;
