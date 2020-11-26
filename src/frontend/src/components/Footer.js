import { Col, Container, Row } from 'react-bootstrap';

import React from 'react';

const Footer = () => (
    <Container className="footer pt-5 pb-5 mt-5" fluid>
        <Container>
            <Row>
                <Col md={3} className="p-2 mr-5">
                    <h3 className="mb-3">MEERTIME</h3>
                    <p className="tagline">
                        MeerTime uses the power of the MeerKAT telescope to explore 
                        fundamental physics and astrophysics via radio pulsar timing.
                    </p>
                </Col>
                <Col md={4} className="p-2 ml-5 mr-5">
                    <h5 className="pt-2 mb-3">External</h5>
                    <ul>
                        <li>
                            <a href="https://gwdc.org.au">Gravitational Wave Data Center (GWDC)</a>
                        </li>
                        <li>
                            <a href="https://meertime.org">MeerTime Public Site</a>
                        </li>
                    </ul>
                </Col>
            </Row>
            <hr/>
            <Row>
                <Col><p>&#169; 2020 MEERTIME. All rights reserved.</p></Col>
            </Row>
        </Container>
    </Container>
);

export default Footer;
