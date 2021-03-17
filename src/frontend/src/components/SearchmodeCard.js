import { Button, Card, Col, Row } from 'react-bootstrap';

import Link from 'found/Link';
import React from 'react';
import { kronosLink } from '../helpers';

const JobCard = ({ row }) => 
    <Card className="mb-3 shadow-md job-card" data-testid="job-card">
        <Card.Body>
            <Card.Title><span className="mr-3">{row.jname}</span> {row.proposalShort}</Card.Title>
            <Row>
                <Col md={3}>
                    <p className="subtitle-1 text-primary-600 mb-2">Observations</p>
                    <p>{row.nobs} in {row.timespan} days</p>
                    <p className="overline mb-1">Last</p>
                    <p>{row.last}</p>
                    <p className="overline mb-1">First</p>
                    <p>{row.first}</p>
                </Col>
            </Row>
        </Card.Body>
        <Card.Footer>
            <Link 
                to={`/search/${row.projectKey}/${row.jname}/`} 
                className='mr-2'
                size='sm' 
                variant="link" 
                as={Button}>
                          View all observations 
            </Link>
            <Button 
                size="sm"
                as="a"
                href={kronosLink(row.lastBeam, row.jname, row.last)}
                variant="link"> 
                        View Kronos 
            </Button>
        </Card.Footer>
    </Card>;

export default JobCard;
