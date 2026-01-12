import { Col, Container, Row } from "react-bootstrap";

import React from "react";

const Footer = () => (
  <Container className="footer pt-5 pb-5 mt-5" fluid>
    <Container>
      <Row>
        <Col md={4} className="p-2">
          <h3 className="mb-3">The Pulsar Portal</h3>
          <p className="tagline">
            The MeerKAT and Molonglo telescopes explore fundamental physics and
            astrophysics via radio pulsar timing.
          </p>
        </Col>
        <Col md={4} className="p-2">
          <h5 className="pt-2 mb-3">External</h5>
          <ul>
            <li>
              <a href="https://gwdc.org.au">
                Gravitational Wave Data Center (GWDC)
              </a>
            </li>
            <li>
              <a href="http://meertime.org">MeerTime Public Site</a>
            </li>
          </ul>
        </Col>
        <Col md={4} className="p-2">
          <h5 className="pt-2 mb-3">Data</h5>
          <ul>
            <li>
              <a href="/data-disclaimer/">Data Information and Disclaimer</a>
            </li>
            <li>
              <a href="/data-usage/">Data Usage Policy</a>
            </li>
            <li>
              <a href="/contact-us/">Report Issue / Contact Us</a>
            </li>
          </ul>
        </Col>
      </Row>
      <hr />
      <Row>
        <Col>
          <p>&#169; 2026 The Pulsar Portal. All rights reserved.</p>
        </Col>
      </Row>
    </Container>
  </Container>
);

export default Footer;
