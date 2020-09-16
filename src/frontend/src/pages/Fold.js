import React from 'react';
import { QueryRenderer, graphql } from 'react-relay';
import environment from '../relayEnvironment';
import { Container, Row, Col } from 'react-bootstrap';
import ListControls from '../components/ListControls';

const query = graphql`
  query FoldQuery {
    observations {
      id
    }
  }`;

const Fold = () => <Container fluid>
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
  <QueryRenderer
    environment={environment}
    query={query}
    render={({error, props}) => {
      if (error) {
        return <div>{error.message}</div>;
      } else if (props) {
        return <div>This is great!</div>;
      }
      return <div>Loading</div>;
    }}
  />
  </Container>;

export default Fold;
