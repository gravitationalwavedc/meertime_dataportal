import React from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import ListControls from '../components/ListControls';

const Fold = ({pulsars}) => {
  return (
    <Container fluid>
      <Row>
        <Col>
          <h4>Fold Observations</h4>
        </Col>
      </Row>
      <Row>
        <Col>
          <ListControls />
        </Col>
      </Row>
      {pulsars.map(pulsar => <Card key={pulsar.jname}>{pulsar.jname}</Card>)}
    </Container>
  );
}

export default Fold;
