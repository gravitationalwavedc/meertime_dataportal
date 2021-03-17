import { Button, Card, Col, Image, Row } from 'react-bootstrap';

import Link from 'found/Link';
import React from 'react';
import image404 from '../assets/images/image404.png';
import { meerWatchLink } from '../helpers';

const SessionCard = ({ row }) => 
    <Card className="mb-3 shadow-md job-card" data-testid="job-card">
        <Card.Body>
            <Card.Title><span className="mr-3">{row.jname}</span> {row.proposalShort}</Card.Title>
            <Row>
                <Col md={3}>
                    <p className="overline mb-1">UTC</p>
                    <p>{row.utc}</p>
                    <p className="overline mb-1">Backend S/N</p>
                    <p>{row.snrSpip}</p>
                </Col>
                <Col md={3}>
                    <p className="overline mb-1">Integration</p>
                    <p>{row.length}</p>
                    <p className="overline mb-1">Frequency</p>
                    <p>{row.frequency}</p>
                </Col>
                <Col>
                    <Image 
                        rounded 
                        fluid 
                        src={row.profile.length > 0 ? `http://localhost:8000/media/${row.profile}` : image404}/> 
                </Col>
                <Col>
                    <Image 
                        rounded 
                        fluid 
                        src={row.profile.length > 0 ? `http://localhost:8000/media/${row.phaseVsTime}` : image404}/>
                </Col>
                <Col>
                    <Image 
                        rounded 
                        fluid 
                        src={row.profile.length > 0 ? `http://localhost:8000/media/${row.phaseVsFrequency}` : image404}/>
                </Col>
            </Row>
        </Card.Body>
        <Card.Footer>
            <Link 
                to={`/fold/${row.projectKey}/${row.jname}/`} 
                className='mr-2'
                size='sm' 
                variant="link" 
                as={Button}>
                          View all observations 
            </Link>
            <Link 
                to={`/${row.jname}/${row.utc}/${row.beam}/`} 
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

export default SessionCard;
