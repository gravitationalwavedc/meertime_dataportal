import { Button, Card, Col, Row } from 'react-bootstrap';

import Link from 'found/Link';
import React from 'react';
import { meerWatchLink } from '../helpers';

const JobCard = ({ row }) => 
    <Card className="mb-3 shadow-md job-card" data-testid="job-card">
        <Card.Body>
            <Card.Title><span className="mr-3">{row.jname}</span> {row.project}</Card.Title>
            <Row>
                <Col md={3}>
                    <p className="subtitle-1 text-primary-600 mb-2">Observations</p>
                    <p>{row.nobs} in {row.timespan} days</p>
                    <p className="overline mb-1">Last</p>
                    <p>{row.last}</p>
                    <p className="overline mb-1">First</p>
                    <p>{row.first}</p>
                </Col>
                <Col md={3}>
                    <p className="subtitle-1 text-primary-600 mb-2">Signal-to-noise</p>
                    <p>{row.latestSnr} last raw</p>
                    <p className="overline mb-1">Average (5 mins)</p>
                    <p>{row.avgSnr5min ? row.avgSnr5min : 'null'}</p>
                    <p className="overline mb-1">Max (5 mins)</p>
                    <p>{row.maxSnr5min ? row.maxSnr5min : 'null'}</p>
                </Col>
                <Col md={3}>
                    <p className="subtitle-1 text-primary-600 mb-2">Intergration</p>
                    <p>{row.totalTintH} hours total</p>
                    <p className="overline mb-1">Last</p>
                    <p>{row.latestTintM ? row.latestTintM : 'null'}</p>
                </Col>
            </Row>
        </Card.Body>
        <Card.Footer>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/fold/${row.projectKey}/${row.jname}/`} 
                className='mr-2'
                size='sm' 
                variant="link" 
                as={Button}>
                          View all observations 
            </Link>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/${row.jname}/${row.latestObservation}/${row.beam}/`} 
                className='mr-2'
                size='sm' 
                variant="link" 
                as={Button}>
                          View last observation
            </Link>
            <Button 
                size="sm"
                as="a"
                href={meerWatchLink(row.jname)}
                variant="link"> 
                        View MeerWatch
            </Button>
        </Card.Footer>
    </Card>;

export default JobCard;
